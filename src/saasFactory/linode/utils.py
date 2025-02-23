import linode_api4

def get_linode_api_token() -> str:
    """
    Get the Linode API token from user input.

    Returns:
        str: The Linode API token entered by the user.
    """
    api_token = input("Enter your Linode API token: ")
    return api_token