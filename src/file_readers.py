"""Module that contains the file readers classes and interface."""
from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from os import stat

from ijson import kvitems, parse


class FileReader(metaclass=ABCMeta):
    """Interface/Abstract class for the file readers.

    Parameters
    ----------
    path: str
        Directory where the file is located.
    file_name: str
        Name of to the file to read.

    Attributes
    ----------
    file_name: str
        File to process. Take the value of the parameter.
    path: str
        Directory where the file is located.
    headers : str
        Reference of metadata of the files.
    size : float
        Size of the file in MB.
    """

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        """Define the conditions for a class to be a (virtual) subclass

        of this interface.

        Parameters
        ----------
        subclass : FileReader
            The class to check.

        Returns
        -------
        bool
            True if the class meets the conditions, False otherwise.
        """
        return (
            hasattr(subclass, 'get_headers') and callable(subclass.get_headers)
            and hasattr(subclass, 'read_record') and callable(subclass.read_record)
            or NotImplemented)

    def __init__(self, path: str, file_name: str) -> None:
        """Initialize the attributes and verify the file extension."""
        if file_name.endswith(self.extension):
            self.file_name: str = file_name
            self.path: str = path
            self.headers: list[str] = []
            self.size: float = round(stat(f'{path}{file_name}').st_size / (1024 * 1024), 4)  # MB
            return None

    def __str__(self):
        """Retun name of the file and its size in MB."""
        return f"{self.file_name} ({self.size} MB)"

    @abstractmethod
    def get_headers(self) -> None:
        """Read just a part of the file to find the metadata of it.

        Notes
        -----
        Must be override in class that implements the interface.
        """
        raise NotImplementedError()

    @abstractmethod
    def read_record(self, data_by_record: int = 0) -> Iterator[list]:
        """Read the file and returns the content.

        Parameters
        ----------
        data_by_record: int
            Number of data by record This parameter could be used
            in some implementations.
        file_object : file
            The object file to read.
        buffer_size : int
            The size of the buffer to read. By default is 1k.

        Returns
        -------
        Iterator
            Iterator with one data of the file at a time.

        Notes
        -----
        Must be override in class that implements the interface.
        """
        raise NotImplementedError()


class FileReaderFactory:
    """The factory to register and select the correct way to read a

    file based on its extension/format.
    """

    def __init__(self) -> None:
        """Create the dict with File readers already existing."""
        self._formats: dict[str, type[FileReader]] = {
            'csv': CSVFileReader,
            'json': JSONFileReader,
            'xml': XMLFileReader
        }

    def register(self, extension: str, file_reader: type[FileReader]) -> None:
        """Register a new file reader with its corresponding extension.

        Parameters
        ----------
        extension : str
            The extension/format of the file (without dot).
        file_reader : type[FileReader]
            The file reader to register.
        """
        self._formats[extension] = file_reader

    def get_file_reader(self, path: str, file: str) -> type[FileReader]:
        """Retrieve the file reader according the extension file.

        Parameters
        ----------
        file: str
            The file name with extension.
        path: str
            The directory of the file.

        Returns
        -------
        type[FileReader]
            The file reader to use.

        Raises
        ------
        ValueError
            When the extension of the file is not registered.
        """
        extension: str = file.rsplit('.')[-1]
        file_reader: type[FileReader] = self._formats.get(extension)
        if file_reader is None:
            raise ValueError(f"The extension '{extension}' is not supported.")
        return file_reader(path, file)


class CSVFileReader(FileReader):
    """Class that process and read data of CSV files.

    Attributes
    ----------
    extension : str
        Extension of the file including the dot at beginning.
    """

    extension: str = '.csv'

    def get_headers(self) -> None:
        """Get the metadata of the file.

        First raw of data.
        """
        with open(f'{self.path}{self.file_name}', encoding="utf-8") as file:
            line: str = file.readline().rstrip('\n')
            self.headers = line.split(',')

    def read_record(self, data_by_record: int = 0) -> Iterator[list]:
        """Read records lazily: line by line to yield it.

        Parameters
        ----------
        data_by_record: int
            Number of data by record. It isn't used in this
            implementation.

        Returns
        -------
        Iterator
            Iterator with a list related to one data of the file
            at a time.
        """
        with open(f'{self.path}{self.file_name}', encoding="utf-8") as file:
            next(file)
            for line in file:
                yield line.rstrip('\n').split(',')


class JSONFileReader(FileReader):
    """Class that process and read data of JSON files.

    Attributes
    ----------
    extension : str
        Extension of the file including the dot at beginning.
    """

    extension: str = '.json'

    def get_headers(self) -> None:
        """Get the name of the keys that define the data (headers).

        Notes
        -----
        Consider that huge json files can cause memory issues, for
        that reason it is used [1]_ijson package.

        Trusting that all the data has the same metadata, after reading
        the headers of the first element... terminate the method.

        References
        ----------
        .. [1] https://pypi.org/project/ijson/
        """
        begin_headers: bool = False
        # print(f'{self.file_name} - {self.size} MB\n')

        with open(f'{self.path}{self.file_name}', 'rb', encoding="utf-8") as file:
            parser: tuple = parse(file, buf_size=2048)  # Just read 2k for time
            # Prefix: the name of the obj. processed at the moment
            # Event: indicate if an object/array begins (start_) or
            # ends (end_), if a property is be defined (map_key) or when
            # a values is defined, the event is the type of it.
            # Value: the name of the property or the value of it
            for prefix, event, value in parser:
                if begin_headers and event == 'map_key':
                    self.headers.append(value)
                elif begin_headers and event == 'end_map':
                    break
                elif (prefix, event) == ('fields.item', 'start_map'):
                    begin_headers = True

    def read_record(self, data_by_record: int = 0) -> Iterator[list]:
        """Read JSON object by object, thanks to knowing how much data

        there is per object and the JSON structure.
        Ijson is essential to achieve the above.

        Parameters
        ----------
        data_by_record: int
            Number of data by record.

        Returns
        -------
        Iterator
            Iterator with a list related to one data of the file
            at a time.
        """
        raw_data: list[str] = []

        with open(f'{self.path}{self.file_name}', 'rb', encoding="utf-8") as file:
            items_kv: Iterator = kvitems(file, 'fields.item', buf_size=512)  # Just read 512 b for time
            for _, value in items_kv:
                raw_data.append(value)
                if len(raw_data) == data_by_record:
                    yield raw_data
                    raw_data = []


class XMLFileReader(FileReader):
    """Class that process and read data of XML files.

    Parameters
    ----------
    parent_tag: str, optional
        Parent element identify the begin and end of data.
    element_tag: str, optional
        Element identify a part of the data.
    attribute_tag: str, optional
        The elements nodes must contain this attribute as metadata.
    value_tag: str, optional
        Tags that contain the data.

    Attributes
    ----------
    extension : str
        Extension of the file including the dot at beginning.
    """

    extension: str = '.xml'

    def __init__(self, path: str, file_name: str, parent_tag: str = 'objects', element_tag: str = 'object',
                 attribute_tag: str = 'name', value_tag: str = 'value') -> None:
        """Extend the functionality of interface. Initilize attributes

        neccesary to know the structure of the file.
        """
        super().__init__(path, file_name)
        self._parent: str = parent_tag
        self._element: str = element_tag
        self._attribute: str = attribute_tag
        self._value: str = value_tag

    def _read_xml_file_attributes(self, xml_path):
        """Read the xml file to capture the metadata of the tags

        in the first parent tag.

        Attributes
        ----------
        xml_path : str
            Path of the xml file.
        """
        captured_names: list = []
        end_parent = f'</{self._parent}>'
        start_tag: str = f'<{self._element}'
        with open(xml_path, encoding="utf-8") as file:
            for line in file:
                if start_tag in line and self._attribute in line:
                    position: int = line.rfind('=') + 2  # avoid the characters ="
                    name: str = line[position:-3]
                    captured_names.append(name)
                elif end_parent in line:
                    break
        return captured_names

    def get_headers(self) -> None:
        """Get the name of the keys that define the data (headers).

        Notes
        -----
        Trusting that all the data has the same metadata, after reading
        the headers of the first element... terminate the method.
        """
        self.headers = self._read_xml_file_attributes(f'{self.path}{self.file_name}')

    def read_record(self, data_by_record: int = 0) -> Iterator[list]:
        """Read the data in parent tags ('<objects>') one by one.

        Parameters
        ----------
        data_by_record: int
            Number of headers by data. It isn't used in this
            implementation.

        Returns
        -------
        Iterator [list]
            Iterator with a list related to one data of the file
            at a time.

        Notes
        -----
        This implementation to get the data is based on the fact that
        the XML file is a well-formed document. Otherwise the algorithm
        could fail and must be refactored -using commented variables-.
        """
        start_data: bool = False
        captured_records: list = []
        # start_tag_identified: bool = False

        start_parent: str = f'<{self._parent}'
        end_parent: str = f'</{self._parent}'
        value_tag: str = f'<{self._value}>'

        with open(f'{self.path}{self.file_name}', encoding="utf-8") as file:
            next(file)
            for line in file:
                if start_parent in line:
                    start_data = True
                    continue
                if start_data and value_tag in line:
                    position: int = line.find('>') + 1
                    captured_records.append(line[position])
                    continue
                if end_parent in line:
                    start_data = False
                    yield captured_records
                    captured_records = []
