import os
from typing import Optional
from datetime import datetime
from tabulate import tabulate
from saasFactory.utils.globals import CONFIG_FILE_NAME, Emojis
from saasFactory.utils.yaml import YAMLParser
from dotenv import load_dotenv, set_key
from pyfiglet import figlet_format


def printWelcomeMessage() -> None:
    ascii_logo = figlet_format("saasFactory", width=140) 
    ascii_name = figlet_format("Scott Williams", font="digital")
    print(ascii_logo)
    print(f"Created by:\n{ascii_name}")

    


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
                pass
            env_file.close()
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
        config_file_path = os.path.join(project_path, CONFIG_FILE_NAME)
        if os.path.exists(config_file_path):
            print("Project already initialized.")
        else:
            with open(config_file_path, "w") as config_file:
                pass
            config_file.close()
        yaml_file = YAMLParser(config_file_path)
        yaml_file.append({"project_name": project_name})
        yaml_file.append({"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
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
    Adds an environment variable to the .env file in the project directory. Resolves conflicts if the variable already exists.

    Args:
        env_var (str): The name of the environment variable.
        value (str): The value of the environment variable.

    Returns:
        bool: True if the environment variable was added or is present, False otherwise.
    """
    project_root = findProjectRoot()
    if project_root is None:
        print("No project found. Please run this command from the project root.")
        return False

    env_file_path = os.path.join(project_root, ".env")
    try:
        load_dotenv(env_file_path)
        # Check if the environment variable already exists
        with open(env_file_path, "r") as env_file:
            lines = env_file.readlines()
        
            for line in lines:
                if line.startswith(f"{env_var.upper()}="):
                    print(f"Environment variable '{env_var.upper()}' already exists in .env file.")
                    print(f"1. Keep existing value: {line.strip()}")
                    print(f"2. Replace with new value: {env_var.upper()}={value}")
                    choice = input("Choose an option (1 or 2): ").strip()
                    if choice == '1':
                        print("Keeping existing environment variable...")
                        return True
                    elif choice == '2':
                        print("Replacing existing environment variable...")
                        break
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                        return False
           
            set_key(dotenv_path=env_file_path, key_to_set=env_var.upper(), value_to_set=value, quote_mode="never")            
            print(f"Added environment variable '{env_var.upper()}' to .env file.")
            return True

    except Exception as e:
        print(f"Error adding environment variable to .env file: {e}")
        return False
    

def get_user_choice(options:list[str], use_table: bool = False, table_headers: list[str] = None) -> int:
    """
    Display a menu of options and return the user's choice.

    Args:
        options (List[str]): A list of options to choose from.
        use_table (bool): Whether to display the options in a table format.
        table_headers (List[str]): A list of column headers for the table.

    Returns:
        int: The index of the selected option.
    """
    while True:
        print("Choose an option:")
        if use_table:
            print(tabulate(options, headers=table_headers, tablefmt="fancy_grid"))
        else:
            for i, option in enumerate(options):
                print(f"[{i}] {option}")
        try:
            choice = int(input("Enter the number for your choice: "))
            if 0 <= choice < len(options):
                return choice
            else:
                print("Invalid number. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def yes_no_prompt(prompt: str, additional_text:Optional[str] = None) -> bool:
    """
    Display a yes/no prompt and return the user's choice.

    Args:
        prompt (str): The prompt message.
        additional_text (Optional[str]): Additional text to display with the prompt.

    Returns:
        bool: True if the user selects 'yes', False otherwise.
    """
    if additional_text:
       print(additional_text)
    while True:
        response = input(f"{prompt} (y/n): ").lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def mb_to_gb(mb: int) -> int:
    """
    Convert megabytes to gigabytes.
    Args:
        mb (int): The value in megabytes.
    Returns:
        int: The value converted to gigabytes.
    """
    return mb // 1024

def get_api_token_cli(provider: str) -> str:
    """
    Get the Linode API token from user input.
    Returns:
        str: The Linode API token entered by the user.
    """
    api_token = input(f"Enter your {provider} API token: ")
    return api_token