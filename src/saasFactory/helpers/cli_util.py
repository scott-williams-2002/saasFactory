import os
from typing import Any, Dict, List, Tuple
from datetime import datetime


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
    config_file_name = "sf_config.yaml"
    try:
        if os.path.exists(os.path.join(project_path, config_file_name)):
            print("Project already initialized.")
        else:
            config_file_path = os.path.join(project_path, config_file_name)
            with open(config_file_path, "w") as config_file:
                config_file.write(f"project_name: {project_name}\n")
                config_file.write(f"created_at: {datetime.datetime.now()}\n")
            config_file.close()
            print(f"Created sf_config.yaml file in: {config_file_path}")
    except Exception as e:
        print(f"Error creating sf_config.yaml file: {e}")


def findProjectRoot() -> str|None:
    """
    Finds the root directory of the project by looking for the sf_config.yaml file.

    Returns:
        str: The path to the sf_config.yaml file if found, otherwise None.
    """
    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, "sf_config.yaml")
    if os.path.exists(config_path):
        return config_path
    return None