from saasFactory.utils.cli import findProjectRoot, root_dir_error_msg
from saasFactory.utils.globals import CONFIG_FILE_NAME
from saasFactory.utils.yaml import YAMLParser, list_to_dot_notation
from saasFactory.utils.globals import CoolifyKeys
from coolipy import Coolipy
import os
#from coolipy import Coolipy
#from coolipy.models.service import ServiceModelCreate, ServiceModel



class CoolifyClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def connect(self) -> None:
        """
        Grabs Coolify configuration from the user's YAML file. Then creates a Coolify client object.
        """
        project_root = findProjectRoot()
        if project_root is None:
            root_dir_error_msg()
            return
        config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)
        sf_config_parser = YAMLParser(config_file_path)

        coolify_configs = sf_config_parser.get(CoolifyKeys.COOLIFY_CONFIGS_KEY.value)
        if coolify_configs is None:
            print("Coolify configurations not found in the config file.")
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
            print(f"Failed to create Coolify client: {e}")
    def test_connection(self) -> bool: 
        """
        Tests the connection to the Coolify API.
        """
        try:
            self.connect()
            list_servers_res = self.coolify_client.servers.list()
            if list_servers_res.status_code == 200 or list_servers_res.status_code == 201:
                print(f"Successfully connected to Coolify API. Status code: {list_servers_res.status_code}")
                return True
            else:
                print("Failed to connect to Coolify API.")
                return False
        except Exception as e:
            print(f"Failed to connect to Coolify API: {e}")
            return False

#figure out  not having coolipy recognized as a module

#start by creating a deployment key, then prompting the user to add it to their github repo, 
#  then creating a project from dockerfile with dev and prod envs 
#  then see about creating a base next repo with the correct configs for deployment that can be forked 
#  try to use the github cli to do all of this or the github api rather than using the web interface
