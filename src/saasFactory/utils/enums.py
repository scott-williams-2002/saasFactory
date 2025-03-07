from enum import Enum

#Environment Variable Names:
class EnvVarNames(Enum):
    """Environment variable names used in the CLI."""
    VPS_API_TOKEN_ENV_VAR = "VPS_API_TOKEN"
    VPS_ROOT_PASSWORD_ENV_VAR = "VPS_ROOT_PASSWORD"
    COOLIFY_API_TOKEN_ENV_VAR = "COOLIFY_API_TOKEN"

#Configurations Key VPS
class VPSKeys(Enum):
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
    COOLIFY_NAME_KEY = "name"
    COOLIFY_PROJECT_DESCRIPTION_KEY = "description"
    COOLIFY_UUID_KEY = "uuid"

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

#github repos - the last 2 are dummy replace later
class GitHubRepos(Enum):
    SAAS_STARTER = "https://github.com/nextjs/saas-starter.git"
    SAAS_STARTER2 = "https://github.com/nextjsfd/saas-starter.git"
    SAAS_STARTER3 = "https://github.com/ddnextjs/saas-starter.git"