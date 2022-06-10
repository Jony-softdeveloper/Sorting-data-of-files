"""Definition of the classes which use the Factories of the two kind of

File Classes to make the data processing and write the results in a
file.
. The WriteData will be the client of FileGeneratorFactory.
. The ProcessData will be the client of FileReaderFactory.
"""
from collections.abc import Iterator
from itertools import zip_longest

from file_generators import FileGeneratorFactory
from file_readers import FileReaderFactory
from functions import sort_alphanumeric, create_result_directory, order_record


class WriteData:
    """The -client- class that took the processed data and writes it in

    a new file.

    Parameters
    ----------
    base_directory: str, optional
        The directory where a directory 'result' is going to be
        created, the output files are going to be in this last one.
        By default is the data directory: ../data/.
    file_name: str, optional
        The name of the file to be created.
    file_extension: str, optional
        The extension of the file to be created (withoith the dot).

    Attributes
    ----------
    directory: str
        The directory path where files are stored.
        By default, it is 'base_directory/result/'.
    """

    def __init__(self, base_directory: str = '../data/', file_name: str = 'result', extension: str = 'tsv') -> None:
        """Name directory for results and file (and extension of it)."""
        self.directory: str = f'{base_directory}result/'
        try:
            self._file_generator: type[FileGeneratorFactory] = (
                FileGeneratorFactory().get_file_generator(self.directory, file_name, extension))
        except ValueError as no_registered:
            print(f'Error: {no_registered.args[0]}')

    def write_headers(self, headers: list[str]):
        """Open the file (it may be created at the moment) and put

        the metadata in the first line according the extension file.
        """
        create_result_directory(self.directory)
        self._file_generator.set_headers(headers)

    def write_data(self, data: list[list], ):
        """Write the data in the file."""
        self._file_generator.set_data(data)

    def __str__(self) -> str:
        """Return the path and name of the aoutput file."""
        return str(self._file_generator)


class ProcessData:
    """The -client- class that reads the files, sorts the data

    (according the order of the gathered headers) and writes results in
    a new file through the fabrics clases.

    Parameters
    ----------
    path: str
        The location -in the file system- of the files.

    Attributes
    ----------
    headers: list[str]
        The set of headers of all the files without duplicates.
    file_processing_data: dict[str, dict]
        Metadata of the readed files.
        The keys will be the name of each file. Whilst the values are
        other dicts with two keys:
        . header_comparison: tuple[int] - set of boolean values, flags,
        result of compare the headers file against gathered headers in
        attribute 'headers'.
        . rearrangement_needed: bool - True if the headers is file are
        not ordered,so the records from it must be ordered; False
        otherwise.

    Notes
    -----
    In order not to have memory problems, the data of the files are
    obtained through generators.
    """

    def __init__(self, path: str) -> None:
        """Initialize the attributes of the class."""
        self.headers: list[str] = []
        self.file_processing_data: dict[str, dict] = {}

        self._path: str = path
        self._file_names: list[str] = []
        self._headers_by_file: tuple[list] = ()

    def get_headers(self) -> list[str]:
        """Return the value of the attribute 'headers'.

        self.headers: list[str]
            The current value of this attribute.
        """
        return self.headers

    def save_file_name(self, file_name: str) -> None:
        """Save the file name in instance attribute.

        Parameters
        ----------
        file_name: str
            The file name to save.
        """
        self._file_names.append(file_name)

    def get_all_headers(self, files: tuple) -> None:
        """Get the headers of each file.

        Parameters
        ----------
        files: tuple
            The tuple of file lists to process.
        """
        factory: type[FileReaderFactory] = FileReaderFactory()

        for files_by_extension in files:
            for file in files_by_extension:
                try:
                    file_reader = factory.get_file_reader(self._path, file)
                except ValueError as no_registered:
                    print(f'Error: {no_registered.args[0]}')
                else:
                    self.save_file_name(file)
                    file_reader.get_headers()  # Get the headers of the file
                    self._headers_by_file = (*self._headers_by_file, file_reader.headers)

    def sort_headers(self) -> None:
        """Sort the headers of the files avoiding add duplicates.

        The headers are sorted alphabetically.

        Notes
        -----
        The sort algorithm may just read the headers of the 'file.csv'
        which has more of them (Readme.md says there is a 'csv' file
        which has header 'Mz', where 'z' is the maximum value of the
        subscript in all the data files).

        However, the implementation works in case files contain
        different headers, even missing some of them; e.g.: a file that
        contain this headers 'M1' and 'M4' without 'M2' and 'M3'.
        Gather them (avoiding duplicates) and after that sort them.
        """
        is_first_list: bool = True

        for file_headers in self._headers_by_file:
            if is_first_list:  # Add the first headers without check for duplicate
                set_headers: set[str] = set(file_headers)
                is_first_list = False
                continue
            for header in file_headers:
                if header not in set_headers:
                    set_headers.add(header)

        self.headers = sort_alphanumeric(list(set_headers))

    def make_file_processing_data(self) -> None:
        """Fill the attribute class with the information from the

        comparison of the headers file against the set of headers
        gathered (headers attribute).
        Each position of 'header_comparison' will work as flag.
        """
        for file_name, file_headers in zip(self._file_names, self._headers_by_file):
            headers_list: list[int] = []
            for header in self.headers:
                if header in file_headers:
                    headers_list.append(True)
                else:
                    headers_list.append(False)
            self.file_processing_data[file_name] = {
                'header_comparison': tuple(headers_list),
                'rearrangement_needed': file_headers != sort_alphanumeric(file_headers),
            }

    def get_data_generators(self) -> tuple[Iterator]:
        """Obtain the data generators of each file.

        Returns
        -------
        data_generators: tuple[Iterator]
            The set of each data generator: 'read_record' fucntion.

        Notes
        -----
        Stored in a tuple for later unpacking.
        """
        data_generators: tuple[Iterator] = ()
        factory: type[FileReaderFactory] = FileReaderFactory()

        for file, headers in zip(self._file_names, self._headers_by_file):
            data_by_record: int = len(headers) if '.json' in file else 0
            try:
                file_reader = factory.get_file_reader(self._path, file)
            except ValueError as no_registered:
                print(f'Error: {no_registered.args[0]}')
            else:
                data_generator: Iterator[list] = file_reader.read_record(data_by_record)
                data_generators = (*data_generators, data_generator)
        return data_generators

    def process_data(self) -> tuple[bool, list[list]]:
        """Get the records/data, by means of the data generators,

        and rearrangment them when is needed. Finally sort all the
        records based on first header (D1).

        Returns
        -------
        tuple(bool, list[list])
            The first position is a flag to indicate if there was a
            partial data write. The second is the records processed,
            all of them or the last one if any writing has been done.

        Notes
        -----
        Every time the records read exceed 50 thousand, it will be a
        partial write to the output file (avoiding using too much RAM).
        Then only the last read data will be returned.
        """
        data_generators: tuple[Iterator] = self.get_data_generators()
        self.make_file_processing_data()
        sorting: list[str] = []
        partial_write: bool = False

        generated_data: type[zip_longest] = zip_longest(*data_generators)
        for data_tuple in generated_data:
            if len(sorting) > 52000:  # Estimated to use approx 2Gb RAM with python 3.10 (memory-profiler)
                # Write this data in the output file
                file_writer: type[WriteData] = WriteData()
                sorting.sort(key=lambda data: data[0:2])
                print(
                    f"52 thousand records of {len(self._file_names)}have been reading.\n "
                    "Please wait: writing data in 'result' file...")
                file_writer.write_data(sorting)
                sorting = []
                partial_write = True
            for index, data in enumerate(data_tuple):
                if data is not None:
                    if self.file_processing_data[self._file_names[index]]['rearrangement_needed']:
                        data = order_record(data, self._headers_by_file[index])
                    data = self.complete_record(data, index)
                    sorting.append(data)

        # At this point it only sorts by the first three headers: D1-D3
        sorting.sort(key=lambda data: data[0:3])

        return partial_write, sorting

    def complete_record(self, record: list[str], file_position: int) -> list[str | None]:
        """Check the record and complete it if needed to have the same

        length as the set of gathered headers (headers attribute).

        'complete' means that recor/Row doesn't have data to every
        header. So, the empty positions are filled with None.

        Parameters
        ----------
        record: list[str]
            The record to check.
        file_position: int
            Number associated with the reading order of the files.
            Records/rows are read in this same order.

        Returns
        -------
        list[str | None]
            The record filled/completed.

        Notes
        -----
        The record must be ordered according the headers before try to
        complete it.
        """
        record_completed: list[str | None] = []
        file_name: str = self._file_names[file_position]
        header_comparison: tuple[int] = self.file_processing_data[file_name]['header_comparison']
        for data, is_header in zip_longest(record, header_comparison):
            record_completed.append(data if is_header else None)

        return record_completed
