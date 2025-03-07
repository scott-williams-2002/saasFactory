from paramiko import SSHClient, AutoAddPolicy, RSAKey
from dotenv import load_dotenv
import os
from saasFactory.utils.enums import Emojis, EnvVarNames
from saasFactory.utils.cli import root_dir_error_msg, findProjectRoot, print_with_underline
from saasFactory.utils.globals import (
    SSH_KEY_DIR_NAME,
    SSH_KEY_FILE_NAME
)

class SSHConnection:
    def __init__(self, host: str, port:int = 22, username: str = "root", key_encrypted: bool = False) -> None:
        """
        Initialize the SSHConnection class.

        Args:
            host (str): The hostname or IP address of the SSH server.
            port (int): The port number to connect to the SSH server (default is 22).
            username (str): The username to use for authentication (default is "root").
            key_encrypted (bool): Whether to use a password for authentication if the private key is encrypted (default is False).
        """
        self.host = host
        self.port = port
        self.username = username
        self.key_encrypted = key_encrypted
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy()) #this removes the `do you want to add to known hosts?` prompt when connecting

    def grab_connection_credentials(self) -> bool:
        """
        Initializes SSH authentication credentials based on user choices.
        Options are: 
        - private key
        - private key + password if key is encrypted with password

        Returns:
            bool: True if credentials were successfully initialized, False otherwise.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return False
        try:
            if self.key_encrypted:
                load_dotenv(os.path.join(project_root, ".env"))
                self.root_password = os.getenv(EnvVarNames.VPS_ROOT_PASSWORD_ENV_VAR.value)
            else:
                self.root_password = None
            self.private_key_path = os.path.join(project_root, SSH_KEY_DIR_NAME, SSH_KEY_FILE_NAME)
            return True
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error reading SSH credentials: {str(e)}")
            return False
        
    def connect(self) -> bool:
        """
        Connects to the SSH server using the provided credentials.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        if not self.grab_connection_credentials():
            return
        
        try:
            with open(self.private_key_path, "r") as key_file:
                key = RSAKey.from_private_key(
                    file_obj=key_file,
                    password=self.root_password if self.key_encrypted else None
                )
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error reading SSH key: {str(e)}")
            return False
        
        try:
            self.ssh_client.connect(
                hostname=self.host,  
                username=self.username,
                pkey=key,
                port=self.port
            )
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error connecting to SSH server: {str(e)}")
            return False
        return True
    
    def execute_command(self, command: str, logging: bool = False) -> str|None:
        """
        Executes a command on the SSH server.

        Args:
            command (str): The command to execute.
            logging (bool): Whether to print the output of the command. (default is False)

        Returns:
            str|None: The output of the command, or None if an error occurred.
        """
        text_len = print_with_underline(f"{Emojis.ROCKET.value} Executing command: `{command}`")
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            full_output = ""
            if logging:
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        output = stdout.channel.recv(1024).decode()
                        print(output, end="")
                        full_output += output
            print("\n" + "-" * text_len)
            return full_output
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error executing command: {str(e)}")
            print(f"STDERR: {stderr.read().decode()}")
            print("\n" + "-" * text_len)
            return None
        
    def disconnect(self) -> None:
        """
        Disconnects from the SSH server.
        """
        self.ssh_client.close()
        print(f"\n{Emojis.DYNAMITE.value} SSH Connection Terminated.")