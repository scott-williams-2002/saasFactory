from enum import Enum
from tabulate import tabulate

#Files Names:
PROJECT_DIR_NAME_SUFFIX = "_sfy_project" # if user doesn't specify a project name this gets added to the current directory name
CONFIG_FILE_NAME = "sf_config.yaml"
SSH_KEY_FILE_NAME = "sfy_key"

#Folder Names:
SSH_KEY_DIR_NAME = "ssh_keys"

#Environment Variable Names:
VPS_API_TOKEN_ENV_VAR = "VPS_API_TOKEN"
VPS_ROOT_PASSWORD_ENV_VAR = "VPS_ROOT_PASSWORD"
COOLIFY_API_TOKEN_ENV_VAR = "COOLIFY_API_TOKEN"

#Configurations Key VPS
VPS_PROJECT_NAME_KEY = "project_name"
VPS_PROVIDER_KEY = "provider"
VPS_CONFIGS_KEY = "vps_configs" #parent key
LINODE_IMAGE_KEY = "image"
LINODE_REGION_KEY = "region"   
LINODE_TYPE_KEY = "type"
LINODE_LABEL_KEY = "label"
LINODE_ID_KEY = "linode_id"
LINODE_PUBLIC_IP_KEY = "public_ip"

#Configurations Key Coolify
class CoolifyKeys(Enum):
    COOLIFY_CONFIGS_KEY = "coolify_configs" #parent key
    COOLIFY_USE_DOMAIN_KEY = "use_domain" #boolean value
    COOLIFY_DOMAIN_KEY = "domain"
    COOLIFY_USE_HTTPS_KEY = "use_https" #boolean value
    COOLIFY_PORT_KEY = "port"
    COOLIFY_OMIT_PORT_KEY = "omit_port"
    COOLIFY_PROJECTS_PARENT_KEY = "projects" #parent key - since there can be multiple projects on one coolify instance
    COOLIFY_PROJECT_NAME_KEY = "name"
    COOLIFY_PROJECT_DESCRIPTION_KEY = "description"
    COOLIFY_PROJECT_UUID_KEY = "uuid"
    COOLIFY_PKEY_UUID_KEY = "uuid"


#Configurations Raw:
DEFAULT_LINODE_VPS_CONFIG = {
    LINODE_IMAGE_KEY: "linode/ubuntu24.04",
    LINODE_REGION_KEY: "us-central",
    LINODE_TYPE_KEY: "g6-standard-1"
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
    DOLLAR = "💲"
    EXCLAMATION = "❗"
    CLOCK = "⏱️"
    LOCK = "🔒"
    KEY = "🔑"
    DOCS = "📚"

class VPSCommands(Enum):
    UPDATE_CMD = "sudo apt update -y"
    UPGRADE_CMD = "sudo apt upgrade -y"
    COOLIFY_INSTALL_CMD = "curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash"

class LinodeStatus(Enum):
    BOOTING = "booting"
    REBOOTING = "rebooting"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    OFFLINE = "offline"
    SHUTTING_DOWN = "shutting_down"
    BUSY = "busy"



#block messages
POST_COOLIFY_INSTALL_MSG = f"""

You can access your instance dashboard through your Public IP: http://[PUBLIC_IP]:8000.

1. Create your admin login credentials on the dashboard. Make sure you save these somewhere safe. {Emojis.LOCK.value}
2. Start onboarding. When prompted choose localhost (remote server is for distributed setups), and create a new project to finish onobarding.
3. Once logged in and onboarded, navigate to "Keys & Tokens" > "API Tokens" to create and save a new token with specified permissions. {Emojis.KEY.value}
4. For saasFactory to function, we need "read", "write", and "deploy" permissions. {Emojis.CHECK_MARK.value}

Refer to the Coolify documentation for more information: https://coolify.ios/docs 📚


You can now continue with the following steps to complete your setup:

1. Run `sfy coolify synth` to synthesize the configurations for your Coolify dashboard.
2. Run `sfy coolify github_connect` to connect to your GitHub repository and deploy Dockerized web apps.
3. Run `sfy coolify telegram_connect` to connect a Telegram bot to your Coolify dashboard for notifications.
4. Run `sfy coolify resource` to create and interact with resources in coolify dashboard.
"""



#github stuff
class GitHubRepos(Enum):
    SAAS_STARTER = "https://github.com/nextjs/saas-starter.git"
    SAAS_STARTER2 = "https://github.com/nextjsfd/saas-starter.git"
    SAAS_STARTER3 = "https://github.com/ddnextjs/saas-starter.git"
