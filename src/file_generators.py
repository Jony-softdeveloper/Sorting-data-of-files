"""The interface and classes that permit write different files of data.

Ideally, these files are generated after some data processing.
"""
from abc import ABCMeta, abstractmethod


class FileGenerator(metaclass=ABCMeta):
    """Interface/Abstract class for the generation of new files.

    Parameters
    ----------
    directory: str
        Path where the file will be stored.
    file_name: str
        Name of to the file to create.
    extension: str
        Extension of the file to create (including the dot).

    Attributes
    ----------
    directory: str
        Path where the new files is stored
    file: str
        Path and name of the file to create.
    """

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        """Define the conditions for a class to be a (virtual) subclass

        of this interface.

        Parameters
        ----------
        subclass : FileGenerator
            The class to check.

        Returns
        -------
        bool
            True if the class meets the conditions, False otherwise.
        """
        return(
            hasattr(subclass, 'set_headers') and callable(subclass.set_headers)
            and hasattr(subclass, 'set_data') and callable(subclass.set_data)
            or NotImplemented)

    def __init__(self, directory: str, file_name: str, extension: str) -> None:
        """Initialize the attributes of the file to create."""
        self.file: str = f'{directory}{file_name}.{extension}'

    def __str__(self) -> str:
        """Return the name of the file to create."""
        return self.file

    @abstractmethod
    def set_headers(self, headers: list[str]) -> None:
        """Structure the metadata of the file according the format file.

        Parameters
        ----------
        headers: list[str]
            The list of headers. This

        Notes
        -----
        Must be override in class that implements the interface.
        """
        raise NotImplementedError()

    @abstractmethod
    def set_data(self, data: list[list]) -> None:
        """According the format file, write the data in the file.

        Parameters
        ----------
        data: list[list]
            The list of data to write. Each position of the list,
            other list, is a record/row of the file.

        Notes
        -----
        Must be override in class that implements the interface.
        """


class FileGeneratorFactory:
    """Factory that permit register and select the proper format to

    apply in output file.
    """

    def __init__(self) -> None:
        """Create the dict with the TSV class as pair k-v and where

        other kind of file formats can be added.
        """
        self._formats: dict[str, type[FileGenerator]] = {
            'tsv': TSVFileGenerator,
        }

    def register(self, extension: str, file_generator: type[FileGenerator]) -> None:
        """Register a new type of file with through its extension.

        Parameters
        ----------
        extension : str
            The extension/format of the file (without dot).
        file_generator : type[FileGenerator]
            The new file generator.
        """
        self._formats[extension] = file_generator

    def get_file_generator(self, directory: str, file_name: str, extension: str) -> type[FileGenerator]:
        """Retrieve the correct class to create a new file.

        Parameters
        ----------
        file_name: str
            Name of the file to create. The extension will be added to this
            name, following it a underscore: extension_file_name.
        extension : str
            The extension/format (including dot) of the file to generate.

        Returns
        -------
        type[FileGenerator]
            The file generator to use.

        Raises
        ------
        ValueError
            When the extension of the file is not registered.
        """
        file_generator = self._formats[extension]
        if file_generator is None:
            raise ValueError(f"The extension '{extension}' is not supported.")
        return file_generator(directory, file_name, extension)


class YamlFileGenerator():  # FileGenerator
    """To generate a aoutput file in YAML format.

    Notes
    -----
    Just need to implement this class and registered the format
    in the factory to be able of generate this kind of files.
    """

    extension: str = '.yaml'


class TSVFileGenerator(FileGenerator):
    """Create TSV files writing its headers and data."""

    extension: str = '.tsv'

    def set_headers(self, headers: list[str]) -> None:
        """Open the file, and created if it does not exist, to

        structure the metadata of the file separated by tabs.

        Parameters
        ----------
        headers: list[str]
            Each position of the list is a metadada or header.
        """
        with open(self.file, 'w', encoding="utf-8") as file:
            file.write('\t'.join(headers))
            file.write('\n')

    def set_data(self, data: list[list]) -> None:
        """Write the ordered data in the output tsv file.

        Every data in the record is separated by one tab.

        Parameters
        ----------
        data: list[list]
            The list of ordered data to write. Each position of the list,
            other list, is a record/row of the file.
        """
        with open(self.file, 'a', encoding="utf-8") as file:
            num_records: int = len(data) - 1
            for records_counter, line in enumerate(data):
                for value in line:
                    # if value is not None:
                    file.write(f"{value if value is not None else ''}\t")
                if records_counter < num_records:
                    file.write('\n')
