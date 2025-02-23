import argparse
import os
from saasFactory.helpers.cli_util import createProjectDir, createEnvFile, createSFConfigFile



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
    # `configure` command 
    configure_parser = subparsers.add_parser(
        "vps", help="Create a VPS instance for the project"
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
