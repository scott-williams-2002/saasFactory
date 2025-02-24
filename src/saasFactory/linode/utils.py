import linode_api4
from dotenv import load_dotenv
import os

def get_linode_api_token() -> str:
    """
    Get the Linode API token from user input.

    Returns:
        str: The Linode API token entered by the user.
    """
    api_token = input("Enter your Linode API token: ")
    return api_token

def testLinodeKey(api_token: str) -> bool:
    """
    Test the Linode API token by attempting to create a LinodeClient.

    Args:
        api_token (str): The Linode API token to test.

    Returns:
        bool: True if the Linode API token is valid, False otherwise.
    """
    try:
        client = linode_api4.LinodeClient(api_token)
        users = client.account.users()
        print(f"Key is valid. Authenticated as: {''.join([user.username for user in users])}")
        return True
    except Exception as e:
        print(f"Error creating Linode client: {e}")
        return False
    