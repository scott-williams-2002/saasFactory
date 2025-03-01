import argparse
import os
from dotenv import load_dotenv
from saasFactory.utils.cli import createProjectDir, createEnvFile, createSFConfigFile, findProjectRoot, addEnvVar, get_api_token_cli, printWelcomeMessage, yes_no_prompt, printInitInstructions, root_dir_error_msg
from saasFactory.utils.globals import VPS_API_TOKEN_ENV_VAR, DEFAULT_LINODE_VPS_CONFIG, CONFIG_FILE_NAME, PROJECT_DIR_NAME_SUFFIX, DEFAULT_LINODE_VPS_CONFIG_TABLE, VPS_CONFIGS_KEY, LINODE_PUBLIC_IP_KEY,DEFAULT_LINODE_USERNAME, POST_COOLIFY_INSTALL_MSG, COOLIFY_API_TOKEN_ENV_VAR, DEFAULT_COOLIFY_PORT
from saasFactory.utils.globals import Emojis, VPSCommands, LinodeStatus, CoolifyKeys
from saasFactory.vps.provider import LinodeProvider
from saasFactory.vps.ssh import SSHConnection
from saasFactory.utils.yaml import YAMLParser, list_to_dot_notation
from tabulate import tabulate

"""
EACH CLI Function has Error logging
"""

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
        # can do sfy vps synth -> vps_create_parser
        # cad do sfy vps up -> vps_up_parser (need to be inside root project folder)     
        # can do sfy vps down -> vps_down_parser
        # can do sfy vps status -> 


    vps_parser = subparsers.add_parser(
        "vps", help="Create a VPS instance for the project"
    )
    vps_subparsers = vps_parser.add_subparsers(dest="vps_command", required=True)

    # `vpc synth` command argument parser
    vps_synth_parser = vps_subparsers.add_parser(
        "synth", help="Sythesize a new VPS instance config"
    )
    vps_synth_parser.add_argument(
        "--provider", type=str, help="Cloud provider for the VPS instance",
        required=True
    )
    vps_synth_parser.add_argument(
        "--api_token", type=str, help="VPS Provider API Token",
        required=False
    )

    # `vpc up` command argument parser
    vps_up_parser = vps_subparsers.add_parser(
        "up", help="Start Up the VPS instance"
    )

    # `vpc down` command argument parser
    vps_down_parser = vps_subparsers.add_parser(
        "down", help="Deactivate the VPS instance"
    )

    # `vpc status` command argument parser
    vps_status_parser = vps_subparsers.add_parser(
        "status", help="Check the status of the VPS instance"
    )
#---------------------------------------------------------------------------------------------------------
    # coolify commands
    coolify_parser = subparsers.add_parser(
        "coolify", help="Coolify commands"
    )
    coolify_subparser = coolify_parser.add_subparsers(dest="coolify_command", required=True)

    coolify_install_parser = coolify_subparser.add_parser(
        "install", help="Install coolify on a VPS"
    )

    coolify_synth_parser = coolify_subparser.add_parser(
        "synth", help="Sythesize a new Coolify instance config"
    )
    coolify_synth_parser.add_argument(
        "--api_token", type=str, help="Coolify API Token",
        required=False
    )
    coolify_synth_parser.add_argument(
        "--domain", action='store_true', help="Flag to indicate if a domain should be used for the Coolify instance connection",
        required=False
    )
    coolify_synth_parser.add_argument(
        "--https", action='store_true', help="Flag to indicate if HTTPS should be used for the Coolify instance connection",
        required=False
    )
#---------------------------------------------------------------------------------------------------------
    args = parser.parse_args()


    # Dispatch based on the command
    if args.command == "init":
        handle_init(args)
    elif args.command == "vps":
        if args.vps_command == "synth":
            handle_vps_synth(args)
        elif args.vps_command == "up":
            handle_vps_up(args)
        elif args.vps_command == "down":
            handle_vps_down(args)
        elif args.vps_command == "status":
            handle_vps_status(args)
    elif args.command == "coolify":
        if args.coolify_command == "install":
            handle_coolify_install(args)
        elif args.coolify_command == "synth":
            handle_coolify_synth(args)



def handle_init(args):
    printWelcomeMessage()
    #gather args and create root project folder
    project_path_input = os.path.abspath(args.path)
    if(args.name):
        project_name = args.name
        project_root_folder = createProjectDir(project_name)
        project_relative_folder = project_name + PROJECT_DIR_NAME_SUFFIX
    else:
        project_name = os.path.basename(project_path_input)
        project_root_folder = createProjectDir(os.path.basename(project_path_input))
        project_relative_folder = os.path.basename(project_path_input) + PROJECT_DIR_NAME_SUFFIX

    #call function that creates a .env file and sf_config.yaml in the root project folder
    createEnvFile(project_root_folder)
    createSFConfigFile(project_root_folder, project_name)
    printInitInstructions(project_relative_folder)
    
    
def handle_vps_synth(args):
    if findProjectRoot() is None:
        root_dir_error_msg()
        return
    
    if (args.provider == "linode" or args.provider == "Linode"):
        # get API token either from command args or from user input and add to .env
        linode_api_token = args.api_token if args.api_token is not None else get_api_token_cli(provider="Linode")
        # add the Linode API token to the .env file
        if(not addEnvVar(VPS_API_TOKEN_ENV_VAR, linode_api_token)):
            return
        # create Linode VPS Provider Instance
        linVPS = LinodeProvider(linode_api_token)
        # test the Linode API token 
        if(not linVPS.test_token_client()):
            return 
        # use default configurations for VPS instance
        defaults_choice = yes_no_prompt(
            "Would you like to use default configurations for the VPS instance?",
            additional_text=DEFAULT_LINODE_VPS_CONFIG_TABLE)
        if defaults_choice:
            print("Using default configurations for the VPS instance.")
            if(not linVPS.configure_instance(DEFAULT_LINODE_VPS_CONFIG)):
                print(f"{Emojis.ERROR_SIGN.value} VPS Configuration Failure.")
                return
        else:
            print("Collecting configuration parameters for the VPS instance.")
            if(not linVPS.configure_instance()):
                print(f"{Emojis.ERROR_SIGN.value} VPS Configuration Failure.")
                return
    else:
        print(f"{Emojis.ERROR_SIGN.value} Invalid provider. Please provide a valid provider.")
        return
    
    print(f"\n{Emojis.STAR.value} {args.provider} VPS instance configured successfully!\n")

def handle_vps_up(args):
    if findProjectRoot() is None:
        root_dir_error_msg()
        return
    config_file = os.path.join(findProjectRoot(), CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        print(f"{Emojis.NO_ENTRY_SIGN.value} Project configuration file not found.")
        return
    print(f"{Emojis.CHECK_MARK.value} Config File Found. Spinning up the VPS instance {Emojis.ROCKET.value}{Emojis.ROCKET.value}{Emojis.ROCKET.value}.")

    # create Linode VPS Provider Instance
    load_dotenv(os.path.join(findProjectRoot(), ".env"))
    linVPS = LinodeProvider(os.environ[VPS_API_TOKEN_ENV_VAR])
    linVPS.get_root_password()
    linVPS.create_instance()


def handle_vps_down(args):
    if findProjectRoot() is None:
        root_dir_error_msg()
        return
    config_file = os.path.join(findProjectRoot(), CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        print(f"{Emojis.ERROR_SIGN.value} Project configuration file not found.")
        return
    print(f"{Emojis.CHECK_MARK.value} Config File Found. Destroying the VPS instance.")
    load_dotenv(os.path.join(findProjectRoot(), ".env"))
    linVPS = LinodeProvider(os.environ[VPS_API_TOKEN_ENV_VAR])
    linVPS.destroy_instance()


def handle_vps_status(args):
    if findProjectRoot() is None:
        root_dir_error_msg()
        return
    config_file = os.path.join(findProjectRoot(), CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        print(f"{Emojis.ERROR_SIGN.value} Project configuration file not found.")
        return
    print(f"{Emojis.CHECK_MARK.value} Config File Found. Checking the VPS instance status.")
    load_dotenv(os.path.join(findProjectRoot(), ".env"))
    linVPS = LinodeProvider(os.environ[VPS_API_TOKEN_ENV_VAR])
    linVPS.check_instance_status(log_status=True)

def handle_coolify_install(args):
    if findProjectRoot() is None:
        root_dir_error_msg()
        return
    config_file = os.path.join(findProjectRoot(), CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        print(f"{Emojis.ERROR_SIGN.value} Project configuration file not found.")
        return
    #check if the instance is running
    load_dotenv(os.path.join(findProjectRoot(), ".env"))
    linVPS = LinodeProvider(os.environ[VPS_API_TOKEN_ENV_VAR])
    vps_status = linVPS.check_instance_status(log_status=False)
    if not vps_status == LinodeStatus.RUNNING.value:
        print(f"{Emojis.ERROR_SIGN.value} VPS instance is not running.")
        print(f"Please ensure the VPS instance is running before installing coolify. Current status: {vps_status}")
   
    print(f"{Emojis.CHECK_MARK.value} Attempting SSH connection to the VPS instance.")
    sf_config_parser = YAMLParser(config_file)
    vps_ipv4 = sf_config_parser.get(list_to_dot_notation([VPS_CONFIGS_KEY, LINODE_PUBLIC_IP_KEY]))
    ssh_con = SSHConnection(host=vps_ipv4, username=DEFAULT_LINODE_USERNAME)
    if not ssh_con.connect():
        print(f"{Emojis.ERROR_SIGN.value} SSH Connection Failed.")
        return
    print(f"{Emojis.CHECK_MARK.value} SSH Connection Successful.")
    
    if not yes_no_prompt(f"Those commands will take a while {Emojis.CLOCK.value}  to execute. Are you sure you want to continue?", additional_text="\n\nThe following commands will be executed:\n" + tabulate([[VPSCommands.UPDATE_CMD.value], [VPSCommands.UPGRADE_CMD.value], [VPSCommands.COOLIFY_INSTALL_CMD.value]])):
        print(f"\n{Emojis.DYNAMITE.value} Aborted Coolify Installation.")
        return

    print(f"{Emojis.CHECK_MARK.value} Attempting to install coolify on the VPS instance.\n")
    if not ssh_con.execute_command(VPSCommands.UPDATE_CMD.value, logging=True):
        print(f"{Emojis.ERROR_SIGN.value} VPS Update Failed.")
        return
    if not ssh_con.execute_command(VPSCommands.UPGRADE_CMD.value, logging=True):
        print(f"{Emojis.ERROR_SIGN.value} VPS Upgrade Failed.")
        return
    if not ssh_con.execute_command(VPSCommands.COOLIFY_INSTALL_CMD.value, logging=True):
        print(f"{Emojis.ERROR_SIGN.value} Coolify Installation Failed.")
        return 
    
    print(f"{Emojis.STAR.value} Coolify Installation Successful.")
    ssh_con.disconnect()
    # prompt user to run manual commands to sign into coolify ...
    print(POST_COOLIFY_INSTALL_MSG)    

def handle_coolify_synth(args):
    if findProjectRoot() is None:
        root_dir_error_msg()
        return
    use_domain = args.domain #if true use domain instead of IP
    use_https = args.https #if true use https instead of http
    omit_port = False
    # get API token either from command args or from user input and add to .env
    coolify_api_token = args.api_token if args.api_token is not None else get_api_token_cli(provider="Coolify")
    # add the Coolify API token to the .env file
    if(not addEnvVar(COOLIFY_API_TOKEN_ENV_VAR, coolify_api_token)):
        return
    
    config_file = os.path.join(findProjectRoot(), CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        print(f"{Emojis.ERROR_SIGN.value} Project configuration file not found.")
        return
    sf_config_parser = YAMLParser(config_file)

    # if use domain true ask for domain
    if use_domain:
        endpoint = input("Please enter the domain name for the Coolify instance endpoint: ")
    else:
        endpoint = sf_config_parser.get(list_to_dot_notation([VPS_CONFIGS_KEY, LINODE_PUBLIC_IP_KEY]))
    #ask to use default port or specify a port
    use_default_port = yes_no_prompt("Would you like to use the default port for the Coolify instance?", additional_text=f"Default Port: {DEFAULT_COOLIFY_PORT}")
    if use_default_port:
        port = DEFAULT_COOLIFY_PORT
    else:
        port = input("Please enter the port number to connect to your Coolify instance (Press `Enter` to omit port): ")
        if not port:
            omit_port = True

    coolify_configs = {
        CoolifyKeys.COOLIFY_USE_DOMAIN_KEY.value: use_domain,
        CoolifyKeys.COOLIFY_DOMAIN_KEY.value: endpoint,
        CoolifyKeys.COOLIFY_USE_HTTPS_KEY.value: use_https,
        CoolifyKeys.COOLIFY_OMIT_PORT_KEY.value: omit_port
    }
    if not omit_port:
        coolify_configs[CoolifyKeys.COOLIFY_PORT_KEY.value] = port #adds port to configs if not omitted
    if not sf_config_parser.append(list_to_dot_notation([CoolifyKeys.COOLIFY_CONFIGS_KEY.value]), coolify_configs):
        print(f"{Emojis.ERROR_SIGN.value} Coolify Configuration Failure.")
        return
    
    #attempt to connect to coolify instance
    print(f"{Emojis.CHECK_MARK.value} Attempting to connect to the Coolify instance.")
    print(f"\n{Emojis.STAR.value} Coolify instance configuration successful!\n")

    
        
    


if __name__ == "__main__":
    main()
