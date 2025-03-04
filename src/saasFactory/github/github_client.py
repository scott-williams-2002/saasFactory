from github import Github
import git
import subprocess


class GitHubRepoClient():
    def __init__(self, github_access_token: str) -> None:
        self.gh_token = github_access_token
        self.github_client = Github(self.gh_token)

    def clone_repo(self, repo_url: str, clone_path: str) -> bool:
        try:
            git.Repo.clone_from(repo_url, clone_path)
            return True
        except Exception as e:
            print(f"Failed to clone repository: {e}")
            return False
        
    def create_private_repo(self, repo_name: str) -> bool:
        try:
            self.new_repo = self.github_client.get_user().create_repo(repo_name, private=True)
            self.new_repo_url = self.new_repo.url
            return True
        except Exception as e:
            print(f"Failed to create private repository: {e}")
            if hasattr(e, 'data'):
                print(f"Error details: {e.data}")
            return False
        
    def push_to_repo(self, repo_path: str, repo_name: str) -> bool:
        try:
            user_login = self.github_client.get_user().login
            remote_url = f"https://{user_login}:{self.gh_token}@github.com/{user_login}/{repo_name}.git"
            
            # Remove existing remote origin if it exists
            subprocess.run(["git", "remote", "remove", "origin"], cwd=repo_path, check=False, timeout=10)
            
            subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=repo_path, timeout=10)
            subprocess.run(["git", "add", "."], cwd=repo_path, timeout=10)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, timeout=10)
            subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, timeout=10)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_path, timeout=10)
            return True
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out: {e}")
            return False
        except Exception as e:
            print(f"Failed to push to repository: {e}")
            return False

    def get_repo_url(self) -> str:
        return self.new_repo_url

    def add_deploy_keys(self, key_title: str, key: str) -> bool:
        try:
            self.new_repo.create_key(key_title, key)
            return True
        except Exception as e:
            print(f"Failed to add deploy key: {e}")
            return False

    def push_deploy(self):
        """
        Pushes the project git repo to github and makes an api call to pull the repo on Coolify
        """
        pass 
        
# Example usage
#gh_client = GitHubRepoClient(str(input("Enter your GitHub access token: ")))
#repo_url = str(input("Enter the URL of the repository you want to clone: "))
#clone_path = "./cloned-repo"
#repo_name = "new_test_cli_repo123"
#
#if gh_client.clone_repo(repo_url, clone_path):
#    if gh_client.create_private_repo(repo_name):
#        if gh_client.push_to_repo(clone_path, repo_name):
#            print(f"Successfully pushed to the new private repository '{repo_name}'.")
#        else:
#            print("Failed to push to the new private repository.")
#    else:
#        print("Failed to create the new private repository.")