import linode_api4
from dotenv import load_dotenv
import os
from linode_api4.objects import Image


def get_linode_api_token() -> str:
    """
    Get the Linode API token from user input.

    Returns:
        str: The Linode API token entered by the user.
    """
    api_token = input("Enter your Linode API token: ")
    return api_token

def testLinodeKey(token_env_var: str, project_root: str) -> bool:
    """
    Test the Linode API token by attempting to create a LinodeClient.

    Args:
        token_env_var (str): The name of the Linode API Token environment variable.
        project_root (str): The path to the project root directory.

    Returns:
        bool: True if the Linode API token is valid, False otherwise.
    """
    load_dotenv(os.path.join(project_root, ".env"))
    api_token = os.getenv(token_env_var)
    if api_token is None:
        print("Linode API Token not found in .env file.")
        return False
    try:
        client = linode_api4.LinodeClient(api_token)
        #images = client.images(Image.vendor == "ubuntu")
        #print(f"Images: {''.join([image.label for image in images])}")
        users = client.account.users()
        print(f"Linode API Token is valid. Authenticated as: {''.join([user.username for user in users])}")
        return True
    except Exception as e:
        print(f"Error Validating Linode API Token. Client Error: {e}")
        return False
    
def collectVPSInstanceConfig() -> None:
    """
    Collects the configuration parameters for creating a new Linode instance.

    Returns:
        dict: A dictionary containing the configuration parameters for the new Linode instance.
    """

    instance_config = {}
    instance_config["region"] = input("Enter the Linode region: ")
    instance_config["type"] = input("Enter the Linode instance type: ")
    instance_config["image"] = input("Enter the Linode image: ")
    instance_config["root_pass"] = input("Enter the root password: ")
    return instance_config
