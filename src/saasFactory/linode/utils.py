import linode_api4
from dotenv import load_dotenv
import os
from linode_api4.objects import Image, Type
from linode_api4.paginated_list import PaginatedList
from saasFactory.utils.cli import CONFIG_FILE_NAME, findProjectRoot, get_choice
from saasFactory.helpers.yamlParse import YAMLParser
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


SSH_KEY_DIR_NAME = "ssh_keys"

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
        users = client.account.users()
        print(f"Linode API Token is valid. Authenticated as: {''.join([user.username for user in users])}")
        return True
    except Exception as e:
        print(f"Error Validating Linode API Token. Client Error: {e}")
        return False
    

def getLinodeImageOptions(token_env_var: str, project_root: str, image_vendor: str = "ubuntu") -> list[Image]:
    """
    Get a list of Linode image options available to the user.

    Args:
        token_env_var (str): The name of the Linode API Token environment variable.
        project_root (str): The path to the project root directory.

    Returns:
        list[Image]|None: A list of Linode images available to the user, or None if an error occurred.
    """
    load_dotenv(os.path.join(project_root, ".env"))
    api_token = os.getenv(token_env_var)
    if api_token is None:
        print("Linode API Token not found in .env file.")
        None
    try:
        client = linode_api4.LinodeClient(api_token)
        images = client.images(Image.vendor == image_vendor)
        return images
    except Exception as e:
        print(f"Error getting Linode image options: {e}")
        None
    
def getLinodeRegionOptions(token_env_var: str, project_root: str) -> list[str]|None:
    """
    Get a list of Linode region options available to the user.

    Args:
        token_env_var (str): The name of the Linode API Token environment variable.
        project_root (str): The path to the project root directory.

    Returns:
        list[str]|None: A list of Linode regions available to the user, or None if an error occurred.
    """
    load_dotenv(os.path.join(project_root, ".env"))
    api_token = os.getenv(token_env_var)
    if api_token is None:
        print("Linode API Token not found in .env file.")
        return None
    try:
        client = linode_api4.LinodeClient(api_token)
        regions = client.regions()
        return [region.id for region in regions]
    except Exception as e:
        print(f"Error getting Linode region options: {e}")
        return None
    
def getLinodeTypeOptions(token_env_var: str, project_root: str) -> PaginatedList|None:
    """
    Get a list of Linode plan options (linode types) available to the user.

    Args:
        token_env_var (str): The name of the Linode API Token environment variable.
        project_root (str): The path to the project root directory.

    Returns:
        list[str]|None: A list of Linode types available to the user, or None if an error occurred.
    """
    load_dotenv(os.path.join(project_root, ".env"))
    api_token = os.getenv(token_env_var)
    if api_token is None:
        print("Linode API Token not found in .env file.")
        return None
    try:
        client = linode_api4.LinodeClient(api_token)
        plans = client.linode.types()
        return plans
    except Exception as e:
        print(f"Error getting Linode type options: {e}")
        return None
    
def mb_to_gb(mb: int) -> int:
    """
    Convert megabytes to gigabytes.

    Args:
        mb (int): The value in megabytes.

    Returns:
        int: The value converted to gigabytes.
    """
    return mb // 1024


def generate_ssh_key_pair(key_name: str, passphrase: str = None) -> str|None:
    """
    Generate an SSH key pair and return the public key in Linode-compatible format.
    
    Args:
        key_name (str): Name for the key pair files
        key_dir (str): Directory to save keys (default: ssh_keys)
        passphrase (str): Optional passphrase for private key encryption
    
    Returns:
        str: Public key string in Linode-compatible format
    """
    # create key_dir in project directory
    project_root = findProjectRoot()
    if project_root is None:
        print("No project found. Please run this command from the project root.")
        return None
    key_dir = os.path.join(project_root, SSH_KEY_DIR_NAME)
    
    if not os.path.exists(key_dir):
        os.makedirs(key_dir, mode=0o700) #mode 0o700: rwx for owner only
    
    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption()
    )
    
    # Serialize public key
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    
    # Write keys to files
    private_path = os.path.join(key_dir, f"{key_name}")
    public_path = os.path.join(key_dir, f"{key_name}.pub")
    
    with open(private_path, 'wb') as f:
        f.write(private_pem)
    os.chmod(private_path, 0o600)
    
    with open(public_path, 'wb') as f:
        f.write(public_key)
    
    return public_key.decode('utf-8')

def addLinodeConfigs(token_env_var: str, configsDict: Optional[dict] = None) -> bool:
    """
    Add Linode configurations to the sf_config.yaml file in the project root directory.

    Args:
        token_env_var (str): The name of the Linode API Token environment variable.
        configsDict (Optional[dict]): A dictionary containing Linode configurations.

    Returns:
        bool: True if the configurations were added successfully, False otherwise.
    """
    project_root = findProjectRoot()
    if project_root is None:
        print("No project found. Please run this command from the project root.")
        return False
    
    config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
    sf_config_parser = YAMLParser(config_file_path)

    if configsDict is not None:
        default_configs = {
            "provider": "linode",
            "vps_configs": configsDict
        }
        if not sf_config_parser.append(default_configs):
            print("Error adding Linode configurations to sf_config.yaml file.")
            return False
        return True
    else:
        images = getLinodeImageOptions(token_env_var, project_root)
        regions = getLinodeRegionOptions(token_env_var, project_root)
        types = getLinodeTypeOptions(token_env_var, project_root)

        if images is None or regions is None or types is None:
            print("Error requesting Linode configuration options.")
            return False
        

        image_choice_index = get_choice([image.label for image in images])
        region_choice_index = get_choice(regions)
        type_format_headers = ["#", "vCPUs", "RAM (GiB)", "Disk (GiB)", "$/hr", "$/mo", "label"]
        type_format_options = [[str(i), str(type.vcpus), str(mb_to_gb(type.memory)), str(mb_to_gb(type.disk)), str(type.price.hourly), str(type.price.monthly), type.label] for i, type in enumerate(types)]
        type_choice_index = get_choice(type_format_options, use_table=True, table_headers=type_format_headers)

        print(f"Image: {images[image_choice_index].id}")
        print(f"Region: {regions[region_choice_index]}")
        print(f"Type: {types[type_choice_index]}")
        
        new_configs = {
            "provider": "linode",
            "vps_configs": {
                "image": images[image_choice_index].id,
                "region": regions[region_choice_index],
                "type": types[type_choice_index].id
                
            }
        }
        if not sf_config_parser.append(new_configs):
            print("Error adding Linode configurations to sf_config.yaml file.")
            return False
        return True




    
    
