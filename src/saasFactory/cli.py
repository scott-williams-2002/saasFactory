import argparse

def main():
    parser = argparse.ArgumentParser(
        description="saasFactory is a CLI tool to make Coolify deployment extremely easy."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)


    # `init` command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new saasFactory project"
    )
    init_parser.add_argument(
        "--name", type=str, help="Name of the project", required=True
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
    if args.command == "config":
        handle_config(args)
    elif args.command == "init":
        handle_init(args)
    elif args.command == "delete":
        handle_delete(args)


def handle_config(args):
    print(f"Generating configuration with: {args.config}")


def handle_init(args):
    print(f"Initializing project with name: {args.name}")


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
