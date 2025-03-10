from saasFactory.utils.enums import Emojis

#prints after coolify is installed sucessfully
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
3. Run `sfy coolify resource` to create and interact with resources in coolify dashboard.
"""