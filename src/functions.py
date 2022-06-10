"""General functions for the application."""
from collections.abc import Callable
from glob import glob
import os
import re

from menu_functions import select_directory


def clean_file_path(path: str, list_files: list[str]) -> list[str]:
    """From every file of the list, delete the part of the path to only

    keep the file name (and its extension/format).

    Parameters
    ----------
    path: str
        The path to the directory. The string to be removed from the
        files.
    list_files: list
        The list of files to clean.

    Returns
    -------
    list
        The list of files cleaned.
    """
    return [file.replace(f'{path}', '') for file in list_files]


def are_there_files(list_csv: list, list_json: list, list_xml: list, path: str) -> tuple:
    """Verify if there are files in the list.

    If there is at least one, add the list to the tuple to be returned;
    if not, the tuple is not modified.

    Parameters
    ----------
    list_csv : list
        List of .csv files (it could be empty).
    list_json: list
        List of .json files (it could be empty).
    list_xml: list
        List of .xml files (it could be empty).
    path: str
        The path of the directory where the files are located.

    Returns
    -------
    files: tuple
        The tuple with the lists of found files .
    """
    files: tuple = ()
    files = (*files, clean_file_path(path, list_csv)) if len(list_csv) > 0 else files
    files = (*files, clean_file_path(path, list_json)) if len(list_json) > 0 else files
    files = (*files, clean_file_path(path, list_xml)) if len(list_xml) > 0 else files

    return files


def get_files(directory_path: str) -> tuple:
    """Retrieve a list of files -of interest- in the directory.

    Parameters
    ----------
    directory_path : str
        The path to the directory where the files are located.

    Returns
    -------
    tuple
        It might contains list of files according the extension.
        The first list are .csv files, the second list are .json files
        and the third one is the related to .xml files.
    """
    files_csv: list = glob(f'{directory_path}*.csv')
    files_json: list = glob(f'{directory_path}*.json')
    files_xml: list = glob(f'{directory_path}*.xml')

    return are_there_files(files_csv, files_json, files_xml, directory_path)


def get_files_from_dir() -> tuple[str, tuple]:
    """Get the files from the entered directory.

    Returns
    -------
    tuple[str, tuple]
        A tuple wich first value is the strign of data directory.
        The second value is None, when there's not files with the
        extension .csv, .json or .xml; otherwise, it's a tuple with
        list of files.
    """
    path: str = select_directory()
    files: tuple = get_files(path)
    # print(f'{path=}\n{files=}')
    if len(files) == 0:
        return path, None
    return path, files


def create_result_directory(directory: str) -> None:
    """Create the directory 'result', where output file(s) will be

    stored.

    Parameters
    ----------
    directory: str
        The path, which include the name of it, of the result directory.
    """
    if not os.path.exists(directory):
        try:
            os.mkdir(directory)
        except FileExistsError as file_error:
            print(f'{file_error.args[0]}')


convert: Callable[[str | int], str | int] = (lambda element: int(element) if element.isdigit() else element.upper())


def sort_alphanumeric(strings: list[str], descending: bool = False) -> list[str]:
    """Sort a set of strings that probably are alphanumeric.

    The main idea is to avoid to put 'D1' next to 'D10', when there are
    nine numbers between them.

    Parameters
    ----------
    strings: list[str]
        The original data to be sorted.
    descending: bool, optional
        If True, the strings are sorted in descending order.
        If False, the strings are sorted in ascending order.

    Returns
    -------
    list[str]
        The sorted strings.

    Notes
    -----
    It is based on a stackoverflow answer [1]_.

    References
    ----------
    ..[1] Mark Byers. April 19th, 2010. Question: 'How to sort alpha
    numeric set in python' by mmrs151. Available [online]:
    https://stackoverflow.com/questions/2669059/how-to-sort-alpha-
    numeric-set-in-python
    """
    alphanum_key: Callable[[str], list[str]] = lambda data: [convert(header) for header in re.split('([0-9]+)', data)]

    return sorted(strings, key=alphanum_key, reverse=descending)


def order_record(record: list[str], messy_file_headers: list[str]) -> list[str]:
    """Order each record to follow the alphanumeric order.

    Because the headers have already been sorted this way and
    data not, the record must be rearranged.

    Parameters
    ----------
    record: list[str]
        The record, that have just been read it, to order.
    messy_file_headers: list[str]
        Original headers of the file. By sorting it, it is possible
        to sort the record

    Returns
    -------
    ordered_record: list[str]
        The record ordered according the headers.
    """
    couple = list(zip(messy_file_headers, record))
    couple.sort(key=lambda data: [convert(header_char) for header_char in re.split('([0-9]+)', data[0])])
    _, ordered_record = zip(*couple)

    return list(ordered_record)
