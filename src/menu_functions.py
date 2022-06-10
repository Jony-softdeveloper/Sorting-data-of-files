"""Functions that permit display the menu in console/CLI and the user

interact with the application.
"""
from os import system, name
from typing import NoReturn


def clear_screen() -> None:
    """To clear screen terminal indepently of Operating system."""
    system('cls' if name == 'nt' else 'clear')   # --no-sec


def exit() -> NoReturn:
    """Finish the execution."""
    print('\nThanks for use -Sorting Data of Files- application.')
    raise SystemExit  # Exactly the same to write system.exit


def show_menu() -> None:
    """Show the menu of the application."""
    print('\n\t\t-Sorting Data of Files-\n')
    print('1. Select the data directory.')
    print('2. Sort the data of the files.')
    print('3. Exit.')


def get_option_user() -> int:
    """Get the option of the user.

    Returns
    -------
    option: int
        Number of option selected.
    """
    while True:
        try:
            option: int = int(input("\nChoose one of the options: ").strip())
        except ValueError:
            print('You can only enter numbers between 1 and 4. Please try again.')
            continue
        else:
            if option <= 0 or option > 3:
                print(f"Sorry, there's no an option number {option}. Please retry it.")
                continue
            break
    return option


def select_directory() -> str:
    """Show a series of instructions to select the directory where the

    files are located.

    Returns
    -------
    str
        The string of the entered directory.
    """
    while True:
        use_path: str = input("Do you want to use the files in 'data' directory? (y/n: another key): ").lower().strip()
        if use_path == 'y':
            return '../data/'

        print('\n* NOTE: Please make sure of write the absolute path to the directory.')
        directory_path: str = input("Enter the path to the data files (to sort): ").strip()
        if '/' not in directory_path and '\\' not in directory_path:
            print('\n* ERROR: The path is not valid.')
            retry: str = input('Do you want to try again? (y/n: another key): ').lower().strip()
            if retry == 'y':
                continue
            exit()
        if not directory_path.endswith('/'):
            directory_path = f'{directory_path}/'

        return directory_path
