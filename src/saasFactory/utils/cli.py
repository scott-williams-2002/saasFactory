import os
from typing import Optional
from datetime import datetime
from tabulate import tabulate
from saasFactory.utils.globals import CONFIG_FILE_NAME, PROJECT_DIR_NAME_SUFFIX, Emojis
from saasFactory.utils.yaml import YAMLParser
from dotenv import load_dotenv, set_key
from pyfiglet import figlet_format


def printWelcomeMessage() -> None:
    ascii_logo = figlet_format("saasFactory", width=140) 
    ascii_name = figlet_format("Scott Williams", font="digital")
    print(ascii_logo)
    print(f"Created by:\n{ascii_name}")

def printInitInstructions(projectFolderName: str) -> None:
    print(f"\n{Emojis.STAR.value} Project initialized successfully!\n")
    usage_msg = f"To use the saasFactory CLI, please run the following commands in the project folder '{projectFolderName}':"
    print(f"\n{usage_msg}\n{len(usage_msg) * '-'}")
    print("  1. `sfy vps synth --provider [linode/(more to come)] --api-token [token optional]`")
    print("     - Synthesize the configurations for a project VPS instance.\n")
    print("  2. `sfy vps up`")
    print("     - Start the VPS instance.\n")
    print("  3. `sfy vps down`")
    print("     - Stop the VPS instance.\n")


def createProjectDir(projectName: str) -> str|None:
    """
    Creates a project directory with the given project name.

    Args:
        projectName (str): The name of the project.

    Returns:
        str: The absolute path of the created project directory, or None if an error occurred.
    """
    try:
        project_path = os.path.abspath(f"{projectName}{PROJECT_DIR_NAME_SUFFIX}")
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        print(f"Initializing a new project:  '{projectName}'")
        print(f"------------------------------{len(projectName) * '-'}")
        print(f">>> Created project directory at: {project_path}")
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
            print(f">>> Created .env file at: {env_file_path}")
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
        print(f">>> Created {CONFIG_FILE_NAME} file at: {config_file_path}")
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
        root_dir_error_msg()
        return False

    env_file_path = os.path.join(project_root, ".env")
    try:
        load_dotenv(env_file_path)
        # Check if the environment variable already exists
        with open(env_file_path, "r") as env_file:
            lines = env_file.readlines()
        
            for line in lines:
                if line.startswith(f"{env_var.upper()}="):
                    print(f"-------------------------------------------{len(env_var) * '-'}")
                    print(f"Conflict detected for environment variable '{env_var.upper()}':")
                    print(f"1. Keep existing value: {line.strip()}")
                    print(f"2. Replace with new value: {env_var.upper()}={value}")
                    choice = input("Choose an option (1 or 2): ").strip()
                    if choice == '1':
                        print("Keeping existing environment variable...")
                        print(f"-------------------------------------------{len(env_var) * '-'}")
                        return True
                    elif choice == '2':
                        print("Replacing existing environment variable...")
                        print(f"-------------------------------------------{len(env_var) * '-'}")
                        break
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                        return False
                    
           
            set_key(dotenv_path=env_file_path, key_to_set=env_var.upper(), value_to_set=value, quote_mode="never")            
            print(f">>> Added environment variable '{env_var.upper()}' to .env file.")
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
                print("\n")
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
        print("\n")
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

def get_api_token_cli(provider: str, token_type: str = "API") -> str:
    """
    Get the API token from user input.

    Args:
        provider (str): The provider for which the token is required.
        token_type (str): The type of token required (default: "API").
    Returns:
        str: The API token entered by the user.
    """
    api_token = input(f"Enter your {provider} {token_type} token: ")
    return api_token

def root_dir_error_msg() -> None:
    """
    Print an error message when a command is not run in the project root. 
    """
    print(f"{Emojis.NO_ENTRY_SIGN.value} No project found. Please run this command from the project root.")

def print_with_underline(text: str) -> int:
    """
    Print text with an underline.
    Args:
        text (str): The text to print.
    Returns:
        int: The length of the text.
    """
    print(text)
    print(len(text) * "-")
    return len(text)