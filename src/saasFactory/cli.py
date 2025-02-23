import argparse
def main():
    parser = argparse.ArgumentParser(
        description="TensorPool is the easiest way to use cloud GPUs. https://tensorpool.dev"
    )

    subparsers = parser.add_subparsers(dest="command")
    gen_parser = subparsers.add_parser(
        "config", help="generate a tp-config.toml job configuration"
    )
    gen_parser.add_argument(
        "config", nargs="*", help="Configuration name or natural language prompt"
    )