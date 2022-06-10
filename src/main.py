"""Main module of the 'sorting data of files' application.

Notes
-----
It was programmed in python 3.10.4 (One of the latest versions).
Author: Jonathan García.

The OOP programming paradigm was used to implement the reading and
writing of files. Using the factory pattern to be able of read the
three kinds of files: CSV, JSON and XML;and to be able of write the
data in different formats(at the moment just create TSV files). Also
this pattern permit add formats of files easily, just implementing the
respective interfaces.

The menu and other functions were coded with structured programming.
Creating instance of the client classes (ProcessData and WriteData)
to process the data.

I used PEP 8 to the structure; but the characters' maximum per line it
was fixed in 120. The comments (and docstrings) length is conserved
with a value of 72.
Also, there are type hints in the functions/methods and variables and
variables. Following the PEP 483, 484, 526...

The format of docstrings is NumPy/SciPy, following PEP 257.
"""
from functions import get_files_from_dir
from menu_functions import exit, clear_screen, get_option_user, show_menu
from data_clients import ProcessData, WriteData


def process_headers(processing: type[ProcessData], file_writer: type[WriteData], files: tuple) -> None:
    """Take the headers of all the files, sort them and write them in

    the output file in a suitable format.

    Parameters
    ----------
    processing:type[ProcessData]
        Instance of ProcessData to be able of process the headers.
    file_writer:type[WriteData]
        Instance of WriteData to be able of write the headers.
    files: tuple
        The tuple of file lists to process.

    Notes
    -----
    If the file(s) already exists, it will be overwritten.
    """
    processing.get_all_headers(files)
    processing.sort_headers()

    file_writer.write_headers(processing.get_headers())


def process_data(path: str, files: tuple) -> None:
    """Make all the process of sorting the data of all the files,

    after of create the file and wirte in it the metadada.
    The sorted data will be written in the file in a suitable format.

    Parameters
    ----------
    path: str
        The directory path where files are stored.
    files: tuple
        The tuple of file lists to process.
    """
    # Instance of the "client" classes that make the main work.
    processing: type[ProcessData] = ProcessData(path)
    file_writer: type[WriteData] = WriteData(path)

    process_headers(processing, file_writer, files)
    partial_write, sorted_data = processing.process_data()
    file_writer.write_data(sorted_data)

    print(f"\nThe data have been sorted and written in '{file_writer}'.")


def main():
    """Display the menu and call the functions to process the data."""
    path: str = ''
    data_files: None | tuple = None
    options: dict[int, callable] = {
        1: get_files_from_dir,
        2: process_data,
    }

    while True:
        clear_screen()
        show_menu()
        selected_option: int = get_option_user()

        clear_screen()
        if selected_option == 1:
            path, data_files = options[selected_option]()
            if data_files is None:
                print(f"There is no files with extension .csv, .json or .xml in '{path}'.")
            else:
                continue_process_data: str = input(
                    '\nContinue with the process of sorting? (y/n: another key): ').lower().strip()
                if continue_process_data == 'y':
                    options[2](path, data_files)
        elif selected_option == 2 and data_files is None:
            print('\nYou must select the directory first.')
        elif selected_option == 2:
            options[2](path, data_files)
        elif selected_option == 3:
            exit()
        # After execute the opttion, show:
        to_continue: str = input("\nDo you want to return to the menu? (y/n: another key): ").lower().strip()
        if to_continue == 'y':
            continue
        exit()


if __name__ == '__main__':
    main()
