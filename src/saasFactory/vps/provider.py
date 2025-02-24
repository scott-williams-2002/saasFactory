import linode_api4
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from saasFactory.utils.globals import SSH_KEY_DIR_NAME, VPS_ROOT_PASSWORD_ENV_VAR, CONFIG_FILE_NAME
from saasFactory.utils.cli import findProjectRoot
from saasFactory.utils.cli import addEnvVar

#abstract VPS class
class VPSProvider:
    def __init__(self, api_token: str):
        self.api_token = api_token

    def generate_ssh_key_pair(self,key_name: str, passphrase: str = None) -> str|None:
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
    
    def mb_to_gb(self, mb: int) -> int:
        """
        Convert megabytes to gigabytes.

        Args:
            mb (int): The value in megabytes.

        Returns:
            int: The value converted to gigabytes.
        """
        return mb // 1024
    
    def get_root_password(self, min_lenght: int = 8) -> None:
        """
        Prompts user to enter a VPS root password. Validates and writes password to .env file.

        Args:
            min_lenght (int): Minimum password length (default: 8)

        """
        while True:
            password_input_1 = input("Enter the root password for the VPS: ")
            if len(password) < min_lenght:
                print(f"Password must be at least {min_lenght} characters long.")
            password_input_2 = input("Confirm the root password: ")
            if password_input_1 != password_input_2:
                print("Passwords do not match. Please try again.")
            else:
                password = password_input_1
                break
        
        # Add the root password to the .env file
        if not addEnvVar(VPS_ROOT_PASSWORD_ENV_VAR, password):
            print("Error adding root password to .env file.")
    
    def test_token_client(self):
        """
        Test the Linode API token by creating a Linode client.
        """
        raise
    
    def configure_instance(self, **kwargs: dict) -> None:
        """
        Configure the VPS instance with the given parameters.
        """
        raise NotImplementedError("Subclasses must implement this method.")