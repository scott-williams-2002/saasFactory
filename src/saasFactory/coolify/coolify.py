from base64 import b64encode
import json
from saasFactory.utils.cli import findProjectRoot, root_dir_error_msg, yes_no_prompt, get_user_choice
from saasFactory.utils.globals import CONFIG_FILE_NAME
from saasFactory.utils.yaml import YAMLParser, list_to_dot_notation
from saasFactory.utils.enums import CoolifyKeys, Emojis, GitHubRepos
from saasFactory.utils.globals import DEFAULT_COOLIFY_PROJECT_NAME, DEFAULT_COOLIFY_SERVICE_NAME, DEFAULT_COOLIFY_PROJECT_DESCRIPTION, DEFAULT_COOLIFY_SERVICE_DESCRIPTION, DEFAULT_COOLIFY_PORT, GIT_REPO_DIR_NAME, DEFAULT_NEW_GITHUB_REPO_NAME, DEFAULT_DEPLOY_KEY_PREFIX, DEFAULT_COOLIFY_ENVIRONMENT_NAME
from saasFactory.github.github_client import GitHubRepoClient
from saasFactory.utils.id import generate_random_id
from coolipy import Coolipy
from coolipy.models.private_keys import PrivateKeysModelCreate
from coolipy.models.service import ServiceModelCreate
from tabulate import tabulate
import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat
import http.client
from uuid import uuid4


class CoolifyClient:
    def __init__(self, api_key):
        self.api_key = api_key
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
        self.sf_config_parser = YAMLParser(config_file_path)

    def connect(self) -> None:
        """
        Grabs Coolify configuration from the user's YAML file. Then creates a Coolify client object.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        coolify_configs = self.sf_config_parser.get(CoolifyKeys.COOLIFY_CONFIGS_KEY.value)
        if coolify_configs is None:
            print(f"{Emojis.WARNING_SIGN.value} Coolify configurations not found in the config file.")
            return
        try:
            self.coolify_endpoint = coolify_configs.get(CoolifyKeys.COOLIFY_DOMAIN_KEY.value)
            self.coolify_rest_client = http.client.HTTPConnection(self.coolify_endpoint, DEFAULT_COOLIFY_PORT)
            omit_port = coolify_configs.get(CoolifyKeys.COOLIFY_OMIT_PORT_KEY.value)
            use_https = coolify_configs.get(CoolifyKeys.COOLIFY_USE_HTTPS_KEY.value)
            if not omit_port:
                port = coolify_configs.get(CoolifyKeys.COOLIFY_PORT_KEY.value)
                self.coolify_client = Coolipy(
                    coolify_api_key=self.api_key,
                    coolify_endpoint=self.coolify_endpoint,
                    omit_port=omit_port,
                    http_protocol="https" if use_https else "http",
                    coolify_port=port
                )
            else:
                self.coolify_client = Coolipy(
                    coolify_api_key=self.api_key,
                    coolify_endpoint=self.coolify_endpoint,
                    omit_port=omit_port,
                    http_protocol="https" if use_https else "http",
                )
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create Coolify client: {e}")

    def test_connection(self) -> bool: 
        """
        Tests the connection to the Coolify API.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        try:
            self.connect()
            list_servers_res = self.coolify_client.servers.list()
            if list_servers_res.status_code == 200 or list_servers_res.status_code == 201:
                print(f"{Emojis.CHECK_MARK.value} Successfully connected to Coolify API. Status code: {list_servers_res.status_code}")
                return True
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to connect to Coolify API.")
                return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to connect to Coolify API: {e}")
            return False
        
    def create_project(self, project_name: str = None, project_description: str = None) -> bool:
        """
        Creates a project on Coolify.

        Args:
            project_name (str): The name of the project.
            project_description (str): The description of the project.
        
        Returns:
            bool: True if the project was created successfully, False otherwise. Still returns True if project created but failed to update the config file.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        
        if project_name is None:
            use_default_name = yes_no_prompt(f"Use default Coolify project name '{DEFAULT_COOLIFY_PROJECT_NAME}'?")
            if use_default_name:
                project_name = DEFAULT_COOLIFY_PROJECT_NAME + generate_random_id()
            else:
                project_name = input("Specify your Coolify project name: ")
        if project_description is None:
            use_default_desc = yes_no_prompt(f"Use default Coolify project description '{DEFAULT_COOLIFY_PROJECT_DESCRIPTION}'?")
            if use_default_desc:
                project_description = DEFAULT_COOLIFY_PROJECT_DESCRIPTION
            else:
                project_description = input("Specify your Coolify project description: ")
        try:
            self.connect()
            res = self.coolify_client.projects.create(project_name=project_name, project_description=project_description)
            if res.status_code == 201 or res.status_code == 200:
                append_res = self.sf_config_parser.append_nested(
                    list_to_dot_notation([CoolifyKeys.COOLIFY_CONFIGS_KEY.value, CoolifyKeys.COOLIFY_PROJECTS_PARENT_KEY.value]),
                    [{
                        CoolifyKeys.COOLIFY_NAME_KEY.value: project_name,
                        CoolifyKeys.COOLIFY_PROJECT_DESCRIPTION_KEY.value: project_description,
                        CoolifyKeys.COOLIFY_UUID_KEY.value: res.data.uuid
                    }]
                )
                if not append_res:
                    print(f"{Emojis.ERROR_SIGN.value} Failed to update the config file.")
                    print("Please manually update the config file with the project UUID, name, and description.")

                print(f"{Emojis.STAR.value} Successfully created project '{project_name}' and updated configs.")
                return True
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to create project '{project_name}'.")
                return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create project '{project_name}': {e}")
            return False
        
    def list_projects(self) -> list[dict]:
        """
        Lists all projects on Coolify.

        Returns:
            list[str]: A list of project dictionaries.
        """
        try:
            self.connect()
            res = self.coolify_client.projects.list()
            if res.status_code ==  200 or res.status_code == 201:
                projects = res.data #list of project objects
                return [{
                    CoolifyKeys.COOLIFY_NAME_KEY.value: project.name, 
                    CoolifyKeys.COOLIFY_UUID_KEY.value: project.uuid} 
                    for project in projects]
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to list projects.")
                return []
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to list projects: {e}")
            return []
        
    def list_servers(self) -> list[dict]:   
        """
        Lists servers on Coolify instance

        Returns:
            list[str]: A list of server dictionaries.
        """
        try:
            self.connect()
            res = self.coolify_client.servers.list()
            if res.status_code ==  200 or res.status_code == 201:
                servers = res.data
                return [{
                    CoolifyKeys.COOLIFY_NAME_KEY.value: server.name,
                    CoolifyKeys.COOLIFY_UUID_KEY.value: server.uuid, 
                } for server in servers]
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to list servers.")
                return []
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to list servers: {e}")
            return []
        
    def create_deploy_key(self, project_uuid: str) -> str:
        """
        Creates a deployment key for a project on Coolify.

        Args:
            project_uuid (str): The UUID of the project.

        Returns:
            str: The public key of the deployment key.
        """
        try:
            private_key = ed25519.Ed25519PrivateKey.generate()
            private_bytes = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.OpenSSH,
                encryption_algorithm=NoEncryption()
            )
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to generate private key: {e}")

        encoded_key = b64encode(private_bytes).decode("utf-8")
        key_title = DEFAULT_DEPLOY_KEY_PREFIX + generate_random_id()

        try:
            self.connect()
            res = self.coolify_client.private_keys.create(private_key=PrivateKeysModelCreate(
                description="Deployment key for GitHub",
                name=key_title,
                private_key=encoded_key
            )) 
            if res.status_code == 201 or res.status_code == 200:
                print(f"{Emojis.CHECK_MARK.value} Successfully created deployment key for project '{project_uuid}'.")

                self.key_uuid = res.data[CoolifyKeys.COOLIFY_UUID_KEY.value]
                return private_key.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode("utf-8")
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to create deployment key for project '{project_uuid}'.")
                return None
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create deployment key for project '{project_uuid}': {e}")
            return None
        
    def create_git_resource(self, project_uuid: str, server_uuid: str, source_url: str) -> bool:
        """
        Creates a git resource for a project on Coolify.
        
        Args:
            project_uuid (str): The UUID of the project.
            source_url (str): The URL of the git repository.
            private (bool): Whether the repository is private. (default is True)
            
        Returns:
            bool: True if the git resource was created successfully, False otherwise.
        """
        try:
            # later on try to replace this with coolipy library
            self.connect()     
            payload_dict = {
                "project_uuid": project_uuid,
                "server_uuid": server_uuid,
                "environment_name": DEFAULT_COOLIFY_ENVIRONMENT_NAME,
                "private_key_uuid": self.key_uuid,
                "git_repository": source_url,
                "git_branch": "main",
                "build_pack": "dockerfile",
                "ports_exposes": "3000",
                "git_commit_sha": "HEAD"
            }

            payload = json.dumps(payload_dict)
            headers = {
                'Authorization': f"Bearer {self.api_key}",
                'Content-Type': "application/json"
            }
            self.coolify_rest_client.request("POST", "/api/v1/applications/private-deploy-key", payload, headers)
            res = self.coolify_rest_client.getresponse()
            if res.status == 201 or res.status == 200:
                print(f"{Emojis.CHECK_MARK.value} Successfully created git resource for project '{project_uuid}'.")
                return True
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to create git resource for project '{project_uuid}'.")
                return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create git resource for project '{project_uuid}': {e}")
            return False
        
    def connect_github(self, github_access_token: str) -> None:
        """
        Connects to the user's GitHub account. Look at projects in config yaml and ask which to associate to if not chosen.

        Args:
            github_access_token (str): The GitHub access token.
        
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        
        chosen_repo_url = get_github_url()
        chosen_new_remote_repo_name = get_new_remote_repo_name()
        chosen_project_uuid = get_project_uuid(self.list_projects())
        pub_key = self.create_deploy_key(chosen_project_uuid)
        chosen_server_uuid = get_server_uuid(self.list_servers())
        if chosen_repo_url is None or chosen_project_uuid is None or chosen_server_uuid is None:
            return
        
        try:
            self.github_client = GitHubRepoClient(github_access_token, chosen_new_remote_repo_name, os.path.join(os.getcwd(), GIT_REPO_DIR_NAME))
            self.github_client.clone_repo(chosen_repo_url)
            self.github_client.create_private_repo(chosen_new_remote_repo_name)
            if yes_no_prompt("Remove old .git folder and initialize new git repository?"):
                self.github_client.remove_old_init()
            else:
                print(f"{Emojis.WARNING_SIGN.value} Skipping removal of old .git folder and initialization of new git repository.")
                self.github_client.remove_upstream()
            self.github_client.add_upstream()
            self.github_client.add_commit_push()
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to connect to GitHub: {e}")
            return
        
        deploy_key_name = DEFAULT_DEPLOY_KEY_PREFIX + generate_random_id()
        if not self.github_client.add_deploy_keys(deploy_key_name, pub_key):
            print(f"{Emojis.ERROR_SIGN.value} Failed to add deploy key to GitHub repository.")
            return
    
        try:
            if self.create_git_resource(chosen_project_uuid, chosen_server_uuid, self.github_client.coolify_deploy_repo_url):
                print(f"{Emojis.CHECK_MARK.value} Successfully created GitHub Coolify Deployment Connection. \nGitHub URL: {self.github_client.coolify_deploy_repo_url}")
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create git resource: {e}")
            return
        
    def create_service(self, service_type: str) -> bool:
        """
        Creates a service on Coolify.

        Args:
            service_type (str): The type of the service. Must be one of DEFAULT_RESOURCE_PRODUCT_NAMES.
        
        Returns:
            bool: True if the service was created successfully, False otherwise.
        """
        chosen_project_uuid = get_project_uuid(self.list_projects())
        chosen_server_uuid = get_server_uuid(self.list_servers())
        dummy_destination_uuid = str(uuid4()) # destination_uuid is not used in the create service API call but coolipy still requires it
        try:
            self.connect()
            # Assuming there is a method in coolipy to create a service
            res = self.coolify_client.services.create(ServiceModelCreate(
                type=service_type,
                name=DEFAULT_COOLIFY_SERVICE_NAME + service_type,
                environment_name=DEFAULT_COOLIFY_ENVIRONMENT_NAME,
                project_uuid=chosen_project_uuid,
                server_uuid=chosen_server_uuid,
                instant_deploy=False,
                description=DEFAULT_COOLIFY_SERVICE_DESCRIPTION,
                destination_uuid=dummy_destination_uuid,

            ))
            if res.status_code == 201 or res.status_code == 200:
                print(f"{Emojis.CHECK_MARK.value} Successfully created service '{service_type}'.")
                print(res)
                return True
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to create service '{service_type}'.")
                return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create service '{service_type}': {e}")
            return False



# Functions to get user input for Coolify operations
#---------------------------------------------------

def get_github_url() -> str:
    """
    Prompts the user to either use a premade GitHub repository or enter a custom URL.

    Returns:
        str: The URL of the GitHub repository.
    """
    premade_repo_choices = "Premade repos:\n" + tabulate([[repo.name, repo.value] for repo in GitHubRepos])
    use_premade = yes_no_prompt("Use a premade GitHub repository?", additional_text=premade_repo_choices)
    if use_premade:
        repos_list  = [[str(i), repo.name, repo.value] for i, repo in enumerate(GitHubRepos)]
        repo_choice = get_user_choice(repos_list, use_table=True, table_headers=["#", "Name", "Link"])
        chosen_repo_url = repos_list[repo_choice][2]
    else:
        chosen_repo_url = input("Enter the URL of the GitHub repository you want to associate with Coolify: ")
    return chosen_repo_url

def get_new_remote_repo_name() -> str:
    """
    Prompts the user to either pick the default name for the remote GitHub repository to create or enter a new name.

    Returns:
        str: The name of the new remote repository.
    """
    use_default_name = yes_no_prompt(f"Use default remote repository name: '{DEFAULT_NEW_GITHUB_REPO_NAME}'?")
    if use_default_name:
        return DEFAULT_NEW_GITHUB_REPO_NAME + generate_random_id()
    else:
        return input("Enter the name of the new remote GitHub repository that will be created: ")

def get_project_uuid(projects: list[str]) -> str:
    """
    Prompts the user to choose a project from a list of projects.

    Args:
        projects (list[str]): A list of project dictionaries.
    Returns:
        str: The UUID of the chosen project.
    """
    chosen_project_idx = get_user_choice([[i, project[CoolifyKeys.COOLIFY_NAME_KEY.value]] for i, project in enumerate(projects)], use_table=True, table_headers=["#", "Project Name"])
    chosen_project_uuid = projects[chosen_project_idx][CoolifyKeys.COOLIFY_UUID_KEY.value]
    return chosen_project_uuid

def get_server_uuid(servers: list[str]) -> str:
    """
    Prompts the user to choose a server from a list of servers.

    Args:
        servers (list[str]): A list of server dictionaries.
    Returns:
        str: The UUID of the chosen server.
    """
    if len(servers) == 0:
        print(f"{Emojis.ERROR_SIGN.value} No servers found on Coolify. Please create a server first.")
        return None
    if len(servers) == 1:
        chosen_server_uuid = servers[0][CoolifyKeys.COOLIFY_UUID_KEY.value]
    else:
        chosen_server_idx = get_user_choice([[i, server[CoolifyKeys.COOLIFY_NAME_KEY.value]] for i, server in enumerate(servers)], use_table=True, table_headers=["#", "Server Name"])
        chosen_server_uuid = servers[chosen_server_idx][CoolifyKeys.COOLIFY_UUID_KEY.value]
    return chosen_server_uuid