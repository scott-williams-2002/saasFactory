import yaml
import os
from collections import OrderedDict

class YAMLParser:
    def __init__(self, file_path: str) -> None:
        """
        Initialize the YAMLParser with the path to the YAML file.

        Args:
            file_path (str): Path to the YAML file.
        """
        self.file_path = file_path

    def read(self) -> dict|None:
        """
        Read the contents of the YAML file. 

        Returns:
            dict|None: The data read from the YAML file as a dictionary, or None if the file does not exist.
        """
        try:
            with open(self.file_path, 'r') as file:
                return yaml.safe_load(file) or None
        except FileNotFoundError:
            return None
        
    def get(self, key: str) -> dict|str|None:
        """
        Get the value of a specific key from the YAML file.
        Supports nested keys using dot notation (e.g., "parent.child.key").

        Args:
            key (str): The key to retrieve the value for. Can be nested using dot notation.

        Returns:
            dict|str|None: The value corresponding to the key, or None if the key does not exist.
        """
        data = self.read()
        if data is None:
            return None

        # Handle nested keys
        key_parts = key.split('.')
        current = data

        # Navigate through the nested structure
        for part in key_parts:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]

        return current

    def append(self, data: dict|str, value: any = None) -> bool:
        """
        Append new data to the existing data in the YAML file.
        Supports both dictionaries and dot notation for appending a single key.

        Args:
            data (dict|str): The data to be appended to the YAML file, or a dot notation key.
            value (any): The value to be appended if data is a dot notation key.

        Returns:
            bool: True if the data was successfully appended, False otherwise.
        """
        try:
            current_data = self.read() or OrderedDict()

            if isinstance(data, dict):
                # Convert current_data to OrderedDict to maintain order
                current_data = OrderedDict(current_data)
                # Merge the new data with the existing data
                for key, val in data.items():
                    current_data[key] = val
            elif isinstance(data, str) and value is not None:
                # Handle dot notation key
                key_parts = data.split('.')
                current = current_data

                for part in key_parts[:-1]:
                    if part not in current or not isinstance(current[part], dict):
                        current[part] = OrderedDict()
                    current = current[part]

                current[key_parts[-1]] = value
            else:
                raise ValueError("Invalid input: data must be a dictionary or a dot notation key with a value.")

            with open(self.file_path, 'w') as file:
                yaml.safe_dump(current_data, file, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error appending data to {os.path.basename(self.file_path)}: {e}")
            return False
            
    def remove(self, key: str) -> bool:
        """
        Remove a section of the YAML file based on the key.
        Supports nested keys using dot notation (e.g., "parent.child.key").

        Args:
            key (str): The key to remove from the YAML file. Can be nested using dot notation.

        Returns:
            bool: True if the key was successfully removed, False otherwise.
        """
        try:
            data = self.read()
            if data is None:
                print(f"Error: {os.path.basename(self.file_path)} is empty.")
                return False

            # Handle nested keys
            key_parts = key.split('.')
            current = data
            parent = None
            final_key = key_parts[-1]

            # Navigate through the nested structure
            for i, part in enumerate(key_parts[:-1]):
                if part not in current:
                    print(f"Error: Key path '{'.'.join(key_parts[:i+1])}' not found in {os.path.basename(self.file_path)}.")
                    return False
                parent = current
                current = current[part]

            # Check if the final key exists in the current level
            if final_key not in current:
                print(f"Error: Key '{key}' not found in {os.path.basename(self.file_path)}.")
                return False

            # Remove the key
            if parent is None:
                del data[final_key]
            else:
                del current[final_key]

            # Save the modified data
            with open(self.file_path, 'w') as file:
                yaml.safe_dump(data, file, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error removing key '{key}' from {os.path.basename(self.file_path)}: {e}")
            return False


def list_to_dot_notation(data: list[str]) -> str:
    """
    Convert a list of strings to a string using dot notation. Used for indexing nested keys in YAML files.

    Args:
        data (list[str]): The list of strings to convert.

    Returns:
        str: The resulting string using dot notation.
    """
    return '.'.join(data)