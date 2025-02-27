#Files Names:
from enum import Enum
from tabulate import tabulate


PROJECT_DIR_NAME_SUFFIX = "_sfy_project" # if user doesn't specify a project name this gets added to the current directory name
CONFIG_FILE_NAME = "sf_config.yaml"
SSH_KEY_FILE_NAME = "sfy_key"

#Folder Names:
SSH_KEY_DIR_NAME = "ssh_keys"

#Environment Variable Names:
VPS_API_TOKEN_ENV_VAR = "VPS_API_TOKEN"
VPS_ROOT_PASSWORD_ENV_VAR = "VPS_ROOT_PASSWORD"

#Configurations Keys:
VPS_PROJECT_NAME_KEY = "project_name"
VPS_PROVIDER_KEY = "provider"
VPS_CONFIGS_KEY = "vps_configs"
LINODE_IMAGE_KEY = "image"
LINODE_REGION_KEY = "region"   
LINODE_TYPE_KEY = "type"
LINODE_LABEL_KEY = "label"
LINODE_ID_KEY = "linode_id"
LINODE_PUBLIC_IP_KEY = "public_ip"

#Configurations Raw:
DEFAULT_LINODE_VPS_CONFIG = {
    LINODE_IMAGE_KEY: "linode/ubuntu24.04",
    LINODE_REGION_KEY: "us-central",
    LINODE_TYPE_KEY: "g6-standard-1"
}

#Configurations Text Formatted:
DEFAULT_LINODE_VPS_CONFIG_TEXT = "Here are the default Linode VPS Configs:\n" + "\n".join([f"{key}: {value}" for key, value in DEFAULT_LINODE_VPS_CONFIG.items()])
DEFAULT_LINODE_VPS_CONFIG_TABLE = "Here are the default Linode VPS Configs:\n" + tabulate([[key, value] for key, value in DEFAULT_LINODE_VPS_CONFIG.items()], headers=["", "Default"], tablefmt="fancy_grid")

#Resources Name Prefixes:
LINODE_INSTANCE_PREFIX = "sfy-instance-"

#Emojis:
class Emojis(Enum):
    """Emojis used in the CLI. Use them like `Emoji.CHECK_MARK.value`."""
    CHECK_MARK = "✅"
    WARNING_SIGN = "⚠️"
    ERROR_SIGN = "❌"
    STOP_SIGN = "🛑"
    NO_ENTRY_SIGN = "🚫"
    THUMBS_UP = "👍"
    PARTY_FACE = "🥳"
    STAR = "✨"
    LIGHTBULB = "💡"
    BOMB = "💣"
    DYNAMITE = "🧨"
    ROCKET = "🚀"
    SOON = "🔜"
    LOADING = "🔄️"