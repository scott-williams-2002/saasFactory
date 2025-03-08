from tabulate import tabulate
from saasFactory.utils.enums import VPSKeys, Emojis

#Files Names:
PROJECT_DIR_NAME_SUFFIX = "_sfy_project" # if user doesn't specify a project name this gets added to the current directory name
CONFIG_FILE_NAME = "sf_config.yaml"
SSH_KEY_FILE_NAME = "sfy_key"

#Folder Names:
SSH_KEY_DIR_NAME = "ssh_keys"

#Configurations Raw:
DEFAULT_LINODE_VPS_CONFIG = {
    VPSKeys.LINODE_IMAGE_KEY.value: "linode/ubuntu24.04",
    VPSKeys.LINODE_REGION_KEY.value: "us-central",
    VPSKeys.LINODE_TYPE_KEY.value: "g6-standard-1"
}
DEFAULT_LINODE_USERNAME = "root"
DEFAULT_COOLIFY_PORT = 8000
DEFAULT_COOLIFY_PROJECT_NAME = "sfy-coolify-project"
DEFAULT_COOLIFY_DESCRIPTION = "A project created by saasFactory CLI."

#Configurations Text Formatted:
DEFAULT_LINODE_VPS_CONFIG_TEXT = "Here are the default Linode VPS Configs:\n" + "\n".join([f"{key}: {value}" for key, value in DEFAULT_LINODE_VPS_CONFIG.items()])
DEFAULT_LINODE_VPS_CONFIG_TABLE = "Here are the default Linode VPS Configs:\n" + tabulate([[key, value] for key, value in DEFAULT_LINODE_VPS_CONFIG.items()], headers=["", "Default"], tablefmt="fancy_grid")

#Resources Name Prefixes:
LINODE_INSTANCE_PREFIX = "sfy-instance-"


