#Files Names:
PROJECT_DIR_NAME_SUFFIX = "_sfy_project" # if user doesn't specify a project name this gets added to the current directory name
CONFIG_FILE_NAME = "sf_config.yaml"

#Folder Names:
SSH_KEY_DIR_NAME = "ssh_keys"

#Environment Variable Names:
VPS_API_TOKEN_ENV_VAR = "VPS_API_TOKEN"
VPS_ROOT_PASSWORD_ENV_VAR = "VPS_ROOT_PASSWORD"

#Configurations Raw:
DEFAULT_LINODE_VPS_CONFIG = {
    "image": "linode/ubuntu24.04",
    "region": "us-central",
    "type": "g6-standard-1"
}

#Configurations Text Formatted:
DEFAULT_LINODE_VPS_CONFIG_TEXT = "Here are the default Linode VPS Configs:\n" + "\n".join([f"{key}: {value}" for key, value in DEFAULT_LINODE_VPS_CONFIG.items()])

