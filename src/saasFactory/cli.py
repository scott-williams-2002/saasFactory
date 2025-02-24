import argparse
import os
from saasFactory.helpers.cli_util import createProjectDir, createEnvFile, createSFConfigFile, findProjectRoot, addEnvVar, yes_no_prompt
from saasFactory.linode.utils import get_linode_api_token, testLinodeKey

LINODE_API_TOKEN_ENV_VAR = "LINODE_API_TOKEN"
DEFAULT_LINODE_VPS_CONFIG = {
    "region": "us-central",
    "type": "g6-standard-1",
    "image": "Ubuntu 24.04 LTS"
}
DEFAULT_LINODE_VPS_CONFIG_TEXT = "Here are the default Linode VPS Configs:\n" + "\n".join([f"{key}: {value}" for key, value in DEFAULT_LINODE_VPS_CONFIG.items()])
LINODE_VPS_CONFIG_INPUT_OPTIONS = ["region", "type", "image", "root_pass"]



def main():
    parser = argparse.ArgumentParser(
        description="saasFactory is a CLI tool to make Coolify setup and deployment extremely easy."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
#---------------------------------------------------------------------------------------------------------
    # `init` command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new saasFactory project"
    )
    init_parser.add_argument(
    "--name", type=str, help="Name of the project (defaults to current directory name)",
    required=False
    )
    init_parser.add_argument(
        "--path", type=str, help="Path where the project should be created",
        default="."
    )
#---------------------------------------------------------------------------------------------------------
    # `vps` command 
        # can do sfy vps create -> vps_create_parser
        # cad do sfy vps up -> vps_up_parser
        # can do sfy vps down -> vps_down_parser
        # can do sfy vps list -> vps_list_parser

    vps_parser = subparsers.add_parser(
        "vps", help="Create a VPS instance for the project"
    )
    vps_subparsers = vps_parser.add_subparsers(dest="vps_command", required=True)


    vps_create_parser = vps_subparsers.add_parser(
        "create", help="Create a new VPS instance"
    )
    vps_create_parser.add_argument(
        "--provider", type=str, help="Cloud provider for the VPS instance",
        required=True
    )
    vps_create_parser.add_argument(
        "--name", type=str, help="Name of the VPS instance",
        required=False
    )
    vps_create_parser.add_argument(
        "--api_token", type=str, help="VPS Provider API Token",
        required=False
    )



    # `delete` command
    delete_parser = subparsers.add_parser(
        "delete", help="Delete an existing saasFactory project"
    )
    delete_parser.add_argument(
        "--force", action="store_true", help="Force deletion without confirmation"
    )
    args = parser.parse_args()


    # Dispatch based on the command
    if args.command == "init":
        handle_init(args)
    elif args.command == "vps":
        if args.vps_command == "create":
            handle_vps_create(args)
    elif args.command == "delete":
        handle_delete(args)


def handle_init(args):
    #gather args and create root project folder
    project_path_input = os.path.abspath(args.path)
    project_name = args.name or os.path.basename(project_path_input)
    project_root_folder = createProjectDir(project_name)

    #call function that creates a .env file and sf_config.yaml in the root project folder
    createEnvFile(project_root_folder)
    createSFConfigFile(project_root_folder, project_name)
    
    
def handle_vps_create(args):
    if findProjectRoot() is None:
        print("No project found. Please run this command from the project root.")
        return
    if (args.provider == "linode" or args.provider == "Linode"):
        # get API token either from command args or from user input and add to .env
        linode_api_token = args.api_token if args.api_token is not None else get_linode_api_token()
        # add the Linode API token to the .env file
        if(not addEnvVar(LINODE_API_TOKEN_ENV_VAR, linode_api_token)):
            print("Error adding Linode API token to .env file.")
            return
        # test the Linode API token is valid
        if(not testLinodeKey(LINODE_API_TOKEN_ENV_VAR, findProjectRoot())):
            print("Error validating Linode API token.")
            return
        # use default configurations for VPS instance
        defaults_choice = yes_no_prompt(
            "Would you like to use default configurations for the VPS instance?",
            additional_text=DEFAULT_LINODE_VPS_CONFIG_TEXT)
        if defaults_choice:
            print("Using default configurations for the VPS instance.")
        else:
            print("Collecting configuration parameters for the VPS instance.")
            # collect the configuration parameters for the VPS instance
            #vps_instance_config = collectVPSInstanceConfig()
            #print(f"VPS Instance Configuration: {vps_instance_config}")

    

    else:
        print("Invalid provider. Please provide a valid provider.")
        return
    
    print(f"Creating VPS instance with provider: {args.provider}")
    if args.name:
        print(f"Name of the VPS instance: {args.name}")

def handle_delete(args):
    if args.force:
        print("Deleting project forcefully.")
    else:
        confirmation = input("Are you sure you want to delete the project? (y/n): ")
        if confirmation.lower() == 'y':
            print("Deleting project.")
        else:
            print("Deletion cancelled.")


if __name__ == "__main__":
    main()
