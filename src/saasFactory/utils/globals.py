from enum import Enum
from tabulate import tabulate
from saasFactory.utils.enums import VPSKeys

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

