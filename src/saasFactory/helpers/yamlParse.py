import yaml
import os

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

    def append(self, data: dict) -> bool:
        """
        Append new data to the existing data in the YAML file.

        Args:
            data (dict): The data to be appended to the YAML file.

        Returns:
            bool: True if the data was successfully appended, False otherwise.
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Input data must be a dictionary.")
            current_data = self.read()

            # Merge the new data with the existing data
            merged_data = {**current_data, **data}

            with open(self.file_path, 'w') as file:
                yaml.safe_dump(merged_data, file, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error appending data to {os.path.basename(self.file_path)}: {e}")
            return False
            
