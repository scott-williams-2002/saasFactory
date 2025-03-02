from saasFactory.utils.cli import findProjectRoot, root_dir_error_msg, yes_no_prompt
from saasFactory.utils.globals import CONFIG_FILE_NAME
from saasFactory.utils.yaml import YAMLParser, list_to_dot_notation
from saasFactory.utils.globals import CoolifyKeys, Emojis
from saasFactory.utils.globals import DEFAULT_COOLIFY_PROJECT_NAME, DEFAULT_COOLIFY_DESCRIPTION
from coolipy import Coolipy
import os
#from coolipy import Coolipy
#from coolipy.models.service import ServiceModelCreate, ServiceModel



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

        coolify_configs = self.sf_config_parser.get(CoolifyKeys.COOLIFY_CONFIGS_KEY.value)
        if coolify_configs is None:
            print(f"{Emojis.WARNING_SIGN.value} Coolify configurations not found in the config file.")
            return
        try:
            coolify_endpoint = coolify_configs.get(CoolifyKeys.COOLIFY_DOMAIN_KEY.value)
            omit_port = coolify_configs.get(CoolifyKeys.COOLIFY_OMIT_PORT_KEY.value)
            use_https = coolify_configs.get(CoolifyKeys.COOLIFY_USE_HTTPS_KEY.value)
            if not omit_port:
                port = coolify_configs.get(CoolifyKeys.COOLIFY_PORT_KEY.value)
                self.coolify_client = Coolipy(
                    coolify_api_key=self.api_key,
                    coolify_endpoint=coolify_endpoint,
                    omit_port=omit_port,
                    http_protocol="https" if use_https else "http",
                    coolify_port=port
                )
            else:
                self.coolify_client = Coolipy(
                    coolify_api_key=self.api_key,
                    coolify_endpoint=coolify_endpoint,
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
        try:
            self.connect()
            list_servers_res = self.coolify_client.servers.list()
            if list_servers_res.status_code == 200 or list_servers_res.status_code == 201:
                print(f"{Emojis.STAR.value} Successfully connected to Coolify API. Status code: {list_servers_res.status_code}")
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
        if project_name is None:
            use_default_name = yes_no_prompt(f"Use default Coolify project name '{DEFAULT_COOLIFY_PROJECT_NAME}'?")
            if use_default_name:
                project_name = DEFAULT_COOLIFY_PROJECT_NAME
            else:
                project_name = input("Specify your Coolify project name: ")
        if project_description is None:
            use_default_desc = yes_no_prompt(f"Use default Coolify project description '{DEFAULT_COOLIFY_DESCRIPTION}'?")
            if use_default_desc:
                project_description = DEFAULT_COOLIFY_DESCRIPTION
            else:
                project_description = input("Specify your Coolify project description: ")
        try:
            self.connect()
            res = self.coolify_client.projects.create(project_name=project_name, project_description=project_description)
            if res.status_code == 201 or res.status_code == 200:
                append_res = self.sf_config_parser.append(
                    list_to_dot_notation([CoolifyKeys.COOLIFY_CONFIGS_KEY.value, CoolifyKeys.COOLIFY_PROJECTS_PARENT_KEY.value]),
                    [{
                        CoolifyKeys.COOLIFY_PROJECT_NAME_KEY.value: project_name,
                        CoolifyKeys.COOLIFY_PROJECT_DESCRIPTION_KEY.value: project_description,
                        CoolifyKeys.COOLIFY_PROJECT_UUID_KEY.value: res.data.uuid
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
                    CoolifyKeys.COOLIFY_PROJECT_NAME_KEY.value: project.name, 
                    CoolifyKeys.COOLIFY_PROJECT_UUID_KEY.value: project.uuid} 
                    for project in projects]
            else:
                print(f"{Emojis.ERROR_SIGN.value} Failed to list projects.")
                return []
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to list projects: {e}")
            return []
        
    def connect_github(self, project_name: str = None) -> None:
        """
        Connects to the user's GitHub account. Look at projects in config yaml and ask which to associate to if not chosen.
        """
        pass

#figure out  not having coolipy recognized as a module

#start by creating a deployment key, then prompting the user to add it to their github repo, 
#  then creating a project from dockerfile with dev and prod envs 
#  then see about creating a base next repo with the correct configs for deployment that can be forked 
#  try to use the github cli to do all of this or the github api rather than using the web interface
