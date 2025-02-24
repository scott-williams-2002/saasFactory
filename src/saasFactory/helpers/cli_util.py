import os
import yaml
from typing import Any, Dict, List, Tuple
from datetime import datetime

CONFIG_FILE_NAME = "sf_config.yaml"


def createProjectDir(projectName: str) -> str|None:
    """
    Creates a project directory with the given project name.

    Args:
        projectName (str): The name of the project.

    Returns:
        str: The absolute path of the created project directory, or None if an error occurred.
    """
    try:
        project_path = os.path.abspath(projectName)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        print(f"Initializing project '{projectName}' in: {project_path}")
        return project_path
    except Exception as e:
        print(f"Error creating project directory: {e}")
        return None


def createEnvFile(project_path: str) -> None:
    """
    Creates a .env file in the specified project directory.

    Args:
        project_path (str): The path to the project directory.

    Returns:
        None
    """
    try:
        if os.path.exists(os.path.join(project_path, ".env")):
            print("Project already initialized.")
        else:
            env_file_path = os.path.join(project_path, ".env")
            with open(env_file_path, "w") as env_file:
                env_file.write("# Add environment variables here") #come back to this, I want to pull from env.example later
            print(f"Created .env file in: {env_file_path}")
    except Exception as e:
        print(f"Error creating .env file: {e}")


def createSFConfigFile(project_path: str, project_name: str) -> None:
    """
    Creates an sf_config.yaml file in the specified project directory.

    Args:
        project_path (str): The path to the project directory.
        project_name (str): The name of the project.

    Returns:
        None
    """
    try:
        if os.path.exists(os.path.join(project_path, CONFIG_FILE_NAME)):
            print("Project already initialized.")
        else:
            config_file_path = os.path.join(project_path, CONFIG_FILE_NAME)
            with open(config_file_path, "w") as config_file:
                config_base = {
                    "project_name": project_name,
                    "created_at": datetime.now()
                }
                yaml.dump(config_base, config_file)
            config_file.close()
            print(f"Created {CONFIG_FILE_NAME} file in: {config_file_path}")
    except Exception as e:
        print(f"Error creating {CONFIG_FILE_NAME} file: {e}")


def findProjectRoot() -> str|None:
    """
    Finds the root directory of the project by looking for the sf_config.yaml file.

    Returns:
        str: The path to the project root directory if found, otherwise None.
    """
    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, CONFIG_FILE_NAME)
    if os.path.exists(config_path):
        return current_dir
    return None

def addEnvVar(env_var: str, value: str) -> bool:
    """
    Adds an environment variable to the .env file in the project directory.

    Args:
        env_var (str): The name of the environment variable.
        value (str): The value of the environment variable.

    Returns:
        None
    """
    project_root = findProjectRoot()
    if project_root is None:
        print("No project found. Please run this command from the project root.")
        return False

    env_file_path = os.path.join(project_root, ".env")
    try:
        with open(env_file_path, "a") as env_file:
            env_file.write(f"{env_var.upper()}={value}\n")
        print(f"Added environment variable '{env_var.upper()}' to .env file.")
        return True
    except Exception as e:
        print(f"Error adding environment variable to .env file: {e}")
        return False
    

def get_choice(options):
    """
    Display a menu of options and return the user's choice.

    Args:
        options (List[str]): A list of options to choose from.

    Returns:
        str: The selected option.
    """
    while True:
        print("Choose an option:")
        for i, option in enumerate(options):
            print(f"[{i}] {option}")
        
        try:
            choice = int(input("Enter the number for your choice: "))
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Invalid number. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")
