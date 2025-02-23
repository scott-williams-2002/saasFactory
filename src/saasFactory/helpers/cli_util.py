import os

def createProjectDir(projectName):
    try:
        project_path = os.path.abspath(projectName)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        print(f"Initializing project '{projectName}' in: {project_path}")
        return project_path
    except Exception as e:
        print(f"Error creating project directory: {e}")
        return None


def createEnvFile(project_path):
    try:
        if os.path.exists(os.path.join(project_path, ".env")):
            print("Project already initialized.")
        else:
            env_file_path = os.path.join(project_path, ".env")
            with open(env_file_path, "w") as env_file:
                env_file.write("# Add environment variables here") #come back to this, I want to pull from env.example later
            print(f"Created .env file in: {env_file_path}")
    except Exception as e:
        print(f"Error creating .env file: {e}")
