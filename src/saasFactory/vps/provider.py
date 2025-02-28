from typing import Optional
from dotenv import load_dotenv
from getpass import getpass
from linode_api4 import LinodeClient
from linode_api4.objects import Image, Instance
from linode_api4.paginated_list import PaginatedList
from paramiko import RSAKey
import os
import shutil
from tabulate import tabulate
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from saasFactory.utils.yaml import YAMLParser, list_to_dot_notation
from saasFactory.utils.globals import (
SSH_KEY_DIR_NAME,
VPS_ROOT_PASSWORD_ENV_VAR, 
CONFIG_FILE_NAME, 
VPS_CONFIGS_KEY, 
SSH_KEY_FILE_NAME,
LINODE_IMAGE_KEY,
LINODE_REGION_KEY,
LINODE_TYPE_KEY,
VPS_PROVIDER_KEY,
LINODE_LABEL_KEY,
VPS_PROJECT_NAME_KEY,
LINODE_INSTANCE_PREFIX,
LINODE_ID_KEY,
LINODE_PUBLIC_IP_KEY,
Emojis,
LinodeStatus
)
from saasFactory.utils.cli import findProjectRoot, addEnvVar, get_user_choice, mb_to_gb, yes_no_prompt, root_dir_error_msg

#abstract VPS class
class VPSProvider:
    def __init__(self, api_token: str):
        self.api_token = api_token

    def generate_ssh_key_pair(self, key_name: str, passphrase: str = None) -> str|None:
        """
        Generate an SSH key pair and return the public key in Linode-compatible format.

        Args:
            key_name (str): Name for the key pair files
            passphrase (str): Optional passphrase for private key encryption

        Returns:
            str: Public key string in Linode-compatible format
        """
        # create key_dir in project directory
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return None
        key_dir = os.path.join(project_root, SSH_KEY_DIR_NAME)

        if not os.path.exists(key_dir):
            os.makedirs(key_dir, mode=0o700) #mode 0o700: rwx for owner only

        # Generate RSA key pair using paramiko
        private_key = RSAKey.generate(bits=4096)

        private_path = os.path.join(key_dir, f"{key_name}")
        public_path = os.path.join(key_dir, f"{key_name}.pub")

        # Write private key to file
        private_key.write_private_key_file(private_path, password=passphrase)
        os.chmod(private_path, 0o600)

        # Write public key to file
        with open(public_path, 'w') as f:
            f.write(f"{private_key.get_name()} {private_key.get_base64()}")

        return f"{private_key.get_name()} {private_key.get_base64()}"

    
    
    def get_root_password(self, min_length: int = 8) -> None:
        """
        Prompts user to enter a VPS root password. Validates and writes password to .env file.

        Args:
            min_lenght (int): Minimum password length (default: 8)

        """
        while True:
            password_input_1 = getpass("Enter the root password for the VPS: ")
            if len(password_input_1) < min_length:
                print(f"Password must be at least {min_length} characters long.")
            password_input_2 = getpass("Confirm the root password: ")
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
        Test the Linode API token by creating a VPS client and printing some user info.
        """
        raise
    
    def configure_instance(self, **kwargs: dict) -> bool:
        """
        Configure the VPS instance with the given parameters.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def create_instance(self):
        """
        Create a VPS instance with the configured parameters.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def destroy_instance(self):
        """
        Delete the VPS instance.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    




#Linode VPS provider class
class LinodeProvider(VPSProvider):
    def __init__(self, api_token: str):
        super().__init__(api_token)
        self.linode_client = LinodeClient(self.api_token)

    def getLinodeImageOptions(self, image_vendor: str = "ubuntu") -> list[Image]:
        """
        Get a list of Linode image options available to the user.

        Args:
            image_vendor (str): The vendor of the images to retrieve (default: "ubuntu").

        Returns:
            list[Image]|None: A list of Linode images available to the user, or None if an error occurred.
        """
        try:
            images = self.linode_client.images(Image.vendor == image_vendor)
            return images
        except Exception as e:
            print(f"Error getting Linode image options: {e}")
            None
    
    def getLinodeRegionOptions(self) -> list[str]|None:
        """
        Get a list of Linode region options available to the user.

        Returns:
            list[str]|None: A list of Linode regions available to the user, or None if an error occurred.
        """
        try:
            regions = self.linode_client.regions()
            return [region.id for region in regions]
        except Exception as e:
            print(f"Error getting Linode region options: {e}")
            return None

    def getLinodeTypeOptions(self) -> PaginatedList|None:
        """
        Get a list of Linode plan options (linode types) available to the user.

        Returns:
            list[str]|None: A list of Linode types available to the user, or None if an error occurred.
        """
        try:
            plans = self.linode_client.linode.types()
            return plans
        except Exception as e:
            print(f"Error getting Linode type options: {e}")
            return None
        
    def test_token_client(self):
        """
        Test the Linode API token by using the client to get the user account information.
        """
        try:
            users = self.linode_client.account.users()
            print(f"Linode API Token is valid {Emojis.CHECK_MARK.value}. Authenticated as: {''.join([user.username for user in users])}")
            return True
        except Exception as e:
            print(f"Error Validating Linode API Token. Client Error: {e}")
            return False
        
    def configure_instance(self, configsDict: Optional[dict] = None) -> bool:
        """
        Add Linode configurations to the CONFIG_FILE_NAME file in the project root directory.

        Args:
            token_env_var (str): The name of the Linode API Token environment variable.
            configsDict (Optional[dict]): A dictionary containing Linode configurations.

        Returns:
            bool: True if the configurations were added successfully, False otherwise.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return False
        
        config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
        sf_config_parser = YAMLParser(config_file_path)
    
        if configsDict is not None:
            #add LINODE_INSTANCE_PREFIX to the label
            project_name_config = sf_config_parser.get(VPS_PROJECT_NAME_KEY) if isinstance(sf_config_parser.get(VPS_PROJECT_NAME_KEY), str) else sf_config_parser.get(VPS_PROJECT_NAME_KEY)[VPS_PROJECT_NAME_KEY]
            configsDict[LINODE_LABEL_KEY] = LINODE_INSTANCE_PREFIX + project_name_config
            default_configs = {
                VPS_PROVIDER_KEY: "linode",
                VPS_CONFIGS_KEY: configsDict
            }
            if not sf_config_parser.append(default_configs):
                print("Error adding Linode configurations to sf_config.yaml file.")
                return False
            return True
        else:
            images = self.getLinodeImageOptions()
            regions = self.getLinodeRegionOptions()
            types = self.getLinodeTypeOptions()
    
            if images is None or regions is None or types is None:
                print("Error requesting Linode configuration options.")
                return False
            
    
            image_choice_index = get_user_choice([image.label for image in images])
            region_choice_index = get_user_choice(regions)
            type_format_headers = ["#", "vCPUs", "RAM (GiB)", "Disk (GiB)", "$/hr", "$/mo", "label"]
            type_format_options = [[str(i), str(type.vcpus), str(mb_to_gb(type.memory)), str(mb_to_gb(type.disk)), str(type.price.hourly), str(type.price.monthly), type.label] for i, type in enumerate(types)]
            type_choice_index = get_user_choice(type_format_options, use_table=True, table_headers=type_format_headers)
    
            print("Selected configurations:")
            selected = [[LINODE_IMAGE_KEY, images[image_choice_index].id], [LINODE_REGION_KEY, regions[region_choice_index]], [LINODE_TYPE_KEY, types[type_choice_index]]]
            print(tabulate(selected, headers=["", "Selected"], tablefmt="fancy_grid"))

            project_name_config = sf_config_parser.get(VPS_PROJECT_NAME_KEY) if isinstance(sf_config_parser.get(VPS_PROJECT_NAME_KEY), str) else sf_config_parser.get(VPS_PROJECT_NAME_KEY)[VPS_PROJECT_NAME_KEY]
            
            new_configs = {
                VPS_PROVIDER_KEY: "linode",
                VPS_CONFIGS_KEY: {
                    LINODE_IMAGE_KEY: images[image_choice_index].id,
                    LINODE_REGION_KEY: regions[region_choice_index],
                    LINODE_TYPE_KEY: types[type_choice_index].id,
                    LINODE_LABEL_KEY: LINODE_INSTANCE_PREFIX + project_name_config
                }
            }
            if not sf_config_parser.append(new_configs):
                print("Error adding Linode configurations to sf_config.yaml file.")
                return False
            return True
        
    def create_instance(self) -> None:
        """
        Create a Linode VPS instance with the configured parameters pulled from the CONFIG_FILE_NAME file."""
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        #ensure token is still valid
        self.test_token_client()

        config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
        sf_config_parser = YAMLParser(config_file_path)

        linode_configs = sf_config_parser.get(VPS_CONFIGS_KEY) #change to optional key for read
        print(f"Linode Configurations: {linode_configs}")
        if linode_configs is None:
            print(f"{Emojis.ERROR_SIGN.value} No Linode configurations found.")
            return
        
        image = linode_configs.get(LINODE_IMAGE_KEY)
        region = linode_configs.get(LINODE_REGION_KEY)   
        instance_type = linode_configs.get(LINODE_TYPE_KEY)
        instance_label = linode_configs.get(LINODE_LABEL_KEY)

        if image is None or region is None or instance_type is None or instance_label is None:
            print(f"{Emojis.ERROR_SIGN.value} Error reading Linode configurations.")
            return

        # get root password from .env file
        load_dotenv(os.path.join(project_root, ".env"))
        root_pass = os.getenv(VPS_ROOT_PASSWORD_ENV_VAR)
        if root_pass is None:
            print(f"{Emojis.WARNING_SIGN.value} {VPS_ROOT_PASSWORD_ENV_VAR} not found in .env file. Please make sure it is set.")
            return
        
        ssh_public_key = self.generate_ssh_key_pair(SSH_KEY_FILE_NAME)#, root_pass)
        if ssh_public_key is None:
            print(f"{Emojis.ERROR_SIGN.value} Error generating SSH key pair.")
            return


        new_linode = self.linode_client.linode.instance_create(
            ltype=instance_type,
            region=region,
            image=image,
            label=instance_label,
            root_pass=root_pass,
            authorized_keys=[ssh_public_key]
        )
        print(f"{Emojis.STAR.value} Linode instance successfully created. Please wait a frew minutes for the intance to boot.")
        instance_details = [[LINODE_LABEL_KEY, new_linode.label], [LINODE_PUBLIC_IP_KEY, new_linode.ipv4[0]], [LINODE_ID_KEY, new_linode.id]]
        print(tabulate(instance_details, headers=["", "Details"], tablefmt="fancy_grid"))
        linode_configs = sf_config_parser.get(VPS_CONFIGS_KEY)
        if isinstance(linode_configs, dict):
            linode_configs[LINODE_ID_KEY] = new_linode.id
            linode_configs[LINODE_PUBLIC_IP_KEY] = new_linode.ipv4[0]
            sf_config_parser.remove(VPS_CONFIGS_KEY)
        if( not sf_config_parser.append({VPS_CONFIGS_KEY: linode_configs})):
            print(f"{Emojis.ERROR_SIGN.value} Error adding Linode ID to {CONFIG_FILE_NAME} file.")
            print(f"Please add the following config to the {CONFIG_FILE_NAME} file manually:")
            print(f"    '{LINODE_ID_KEY}: {new_linode.id}'")
            return

    
    def destroy_instance(self) -> None:
        """
        Delete the Linode VPS instance.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        #ensure token is still valid
        self.test_token_client()

        config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
        sf_config_parser = YAMLParser(config_file_path)

        linode_configs = sf_config_parser.get(VPS_CONFIGS_KEY)
        if linode_configs is None:
            print(f"{Emojis.ERROR_SIGN.value} No Linode configurations found.")
            return 
        
        instance_id = linode_configs.get(LINODE_ID_KEY)
        if instance_id is None:
            print(f"{Emojis.ERROR_SIGN.value} Error reading Linode configurations.")
            return
        
        instance_to_delete = self.linode_client.linode.instances(Instance.id == instance_id) #object to call .delete() on
        instance_to_delete_label = instance_to_delete[0].label
        instance_to_delete_id = instance_to_delete[0].id
        if instance_to_delete is None:
            print(f"{Emojis.ERROR_SIGN.value} No Linode instance found with the specified ID.")
            return 
        
        delete = yes_no_prompt("Are you sure you want to permanently delete this instance?", additional_text=f"Instance Label: {instance_to_delete_label}\n")
        if delete:
            try:
                instance_to_delete[0].delete()
                #print(f"Linode instance {instance_to_delete_details.label} deleted.")
                print(f"{Emojis.STAR.value} Linode instance successfully deleted.")
                
            except Exception as e:
                print(f"{Emojis.ERROR_SIGN.value} Error Deleting Linode Instance. Error: {e}")
                return 
            # now deleting associated data from sassFactory project directory
            try: 
                #removing ssh keys and instance ID
                if os.path.exists(os.path.join(project_root, SSH_KEY_DIR_NAME)):
                    print(f"Removing {SSH_KEY_DIR_NAME} folder and its contents.")
                    shutil.rmtree(os.path.join(project_root, SSH_KEY_DIR_NAME))
                    print(f"Removing {LINODE_ID_KEY} and {LINODE_PUBLIC_IP_KEY} from {CONFIG_FILE_NAME} file.")
                    sf_config_parser.remove(list_to_dot_notation([VPS_CONFIGS_KEY, LINODE_ID_KEY]))
                    sf_config_parser.remove(list_to_dot_notation([VPS_CONFIGS_KEY, LINODE_PUBLIC_IP_KEY]))
            except Exception as e:
                print(f"{Emojis.ERROR_SIGN.value} Error deleting SSH keys and/or {LINODE_ID_KEY} from {CONFIG_FILE_NAME} file. Error: {e}")
                return
            
        else:
            print(f"{Emojis.BOMB.value} Instance deletion aborted.")
            return
        
    def check_instance_status(self, log_status: bool = False) -> str|None:
        """
        Check the status of the Linode VPS instance. Returns the status of the instance as a string. 
        Can return the following statuses: running, offline, booting, busy, rebooting, shutting_down, provisioning, deleting, migrating, rebuilding, cloning, restoring, stopped, billing_suspension

        Args:
            log_status (bool): If True, the status of the instance will be printed to the console.

        Returns:
            str: The status of the Linode VPS instance.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        self.test_token_client()
        try:
            config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
            sf_config_parser = YAMLParser(config_file_path)
            linode_configs = sf_config_parser.get(VPS_CONFIGS_KEY)
            instance_id = linode_configs.get(LINODE_ID_KEY)
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error reading Linode configurations. Error: {e}")
            return None
        try:
            instance = self.linode_client.linode.instances(Instance.id == instance_id)[0]
            instance_status = instance.status
            instance_status = instance_status.lower().strip()
            if log_status:
                if instance_status == LinodeStatus.RUNNING.value:
                    print(f"{Emojis.LIGHTBULB.value} Linode instance is {instance_status}.")
                elif instance_status == LinodeStatus.BOOTING.value or instance_status == LinodeStatus.REBOOTING.value or instance_status == LinodeStatus.SHUTTING_DOWN.value or instance_status == LinodeStatus.BUSY.value:
                    print(f"{Emojis.LOADING.value} Linode instance is {instance_status}.")
                elif instance_status == LinodeStatus.PROVISIONING.value:
                    print(f"{Emojis.SOON.value} Linode instance is {instance_status}.")
                elif instance_status is None:
                    print(f"{Emojis.STOP_SIGN.value} Linode instance is either non-existent or has been deleted.")
                    return "offline"
                else:
                    print(f"{Emojis.EXCLAMATION.value} Linode instance is {instance_status}.")
                
            return instance_status  
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error getting Linode instance status. Error: {e}. Instance may be offline.")
            return "offline"
        

           

    