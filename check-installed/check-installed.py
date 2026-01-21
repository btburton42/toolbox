# this is a function to help with uninstalling applications off a users machine.
import os
import sys
import argparse
from pathlib import Path

def fuzzy_match(str1: str, str2: str) -> bool:
    """A simple fuzzy match function that checks if str1 is in str2, case insensitive."""
    return str1.lower() in str2.lower()

def print_dir_contents(type_match: str, directory: str, delete: bool = False):
    """Prints the contents of a directory."""
    emoji = "🍑" if type_match == "exact" else "👍"
    print(f"{type_match} match {emoji}:")
    print(directory)
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                print(os.path.join(root, file))
                if delete:
                    try:
                        os.remove(os.path.join(root, file))
                        print(f"Deleted file: {os.path.join(root, file)}")
                    except Exception as e:
                        print(f"Failed to delete file: {os.path.join(root, file)}. Error: {e}")

    except PermissionError as err:
        print(f"no go match 🚫: {err}")
        pass
    
def main(input_string: str, exact: bool = False, delete: bool = False):
    # first, i want it to check several directories for files related to a fuzzy string input match as an arg
    directories_to_check = [
        '/Library/Application Support/',
        '~/Library/Application Support/',
        '~/Library/Caches/',
        '~/Library/Preferences/',
        '~/Library/Logs/',
        '~/Library/Application State/'
    ]
    # Expand ~ to user home
    expanded_dirs = [os.path.expanduser(d) for d in directories_to_check]
    
    # then i want to print those to the console
    for directory in expanded_dirs:
        if os.path.exists(directory):
            try:
                contents = os.listdir(directory)
            except PermissionError:
                continue
            for item in contents:
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    if input_string.lower() == item.lower():
                            print_dir_contents("exact", full_path, delete)
                    elif fuzzy_match(input_string, item) and not exact:
                            print_dir_contents("fuzzy", full_path, delete)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for installed applications")
    parser.add_argument('app_name', help='The application name to search for')
    parser.add_argument('--exact', action='store_true', help='Match the top directory exactly')
    parser.add_argument('--delete', action='store_true', help='Delete matched files')
    args = parser.parse_args()
    main(args.app_name, exact=args.exact, delete=args.delete)

                # full_path = os.path.join(directory, item)
                # if os.path.isfile(full_path):
                #     # Simple fuzzy match: check if input_string is in filename (case insensitive)
                #     if fuzzy_match(input_string, item):
                #         print(full_path)
                # elif os.path.isdir(full_path):
                #     # Check if subdir name matches
                #     if exact:
                #         if input_string.lower() == item.lower():
                #             # Print all files in this subdir
                #             for root, dirs, files in os.walk(full_path):
                #                 for file in files:
                #                     print(os.path.join(root, file))
                #     else:
                #         if fuzzy_match(input_string, item):
                #             # Print all files in this subdir
                #             for root, dirs, files in os.walk(full_path):
                #                 for file in files:
                #                     print(os.path.join(root, file))
