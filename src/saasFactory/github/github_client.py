from github import Github
import git
import os
import subprocess
from saasFactory.utils.enums import Emojis


class GitHubRepoClient():
    """
    A class to interact with local git and remote GitHub repositories.
    """

    def __init__(self, github_access_token: str, repo_name: str, repo_path) -> None:
        self.gh_token = github_access_token
        self.github_client = Github(self.gh_token)
        self.user_login = self.github_client.get_user().login
        self.repo_path = repo_path
        self.repo_name = repo_name
        self.remote_url = f"https://{self.user_login}:{self.gh_token}@github.com/{self.user_login}/{repo_name}.git"
        self.coolify_deploy_repo_url = "git@github.com:" + self.user_login + "/" + self.repo_name + ".git"

    def clone_repo(self, repo_url: str) -> bool:
        """
        Clones a repository from the specified URL to the specified local path.

        Args:
            repo_url (str): The URL of the repository to clone.
            clone_path (str): The path where the repository should be cloned.
        """
        try:
            git.Repo.clone_from(repo_url, self.repo_path)
            return True
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Error cloning repository: {e}")
            return False
                
    def create_private_repo(self, repo_name: str) -> bool:
        """
        Creates a private remote GitHub repository with the specified name.

        Args:
            repo_name (str): The name of the repository to create.
        Returns:
            bool: True if the repository was successfully created, False otherwise.
        """
        try:
            self.new_repo = self.github_client.get_user().create_repo(repo_name, private=True)
            return True
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to create private repository: {e}")
            if hasattr(e, 'data'):
                print(f"Error details: {e.data}")
            return False
        
    def remove_old_init(self) -> bool:
        """
        Removes the .git folder from the specified repository path and initializes a new git repository.

        Args:
            repo_path (str): The path to the repository.
        Returns:
            bool: True if the .git folder was successfully removed (or never existed) and a new repository was initialized, False otherwise.
        """
        try:
            if os.path.exists(os.path.join(self.repo_path, ".git")):
                subprocess.run(["rm", "-rf", f"{self.repo_path}/.git"], timeout=10)
                subprocess.run(["git", "init"], cwd=self.repo_path, timeout=10)
            return True
        except subprocess.TimeoutExpired as e:
            print(f"{Emojis.CLOCK.value} Command timed out: {e}")
            return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to remove .git folder: {e}")
            return False
        
    def remove_upstream(self) -> bool:
        """
        Removes the upstream remote from the specified repository path.

        Args:
            repo_path (str): The path to the repository.
        Returns:
            bool: True if the upstream remote was successfully removed, False otherwise.
        """
        try: 
            subprocess.run(["git", "remote", "remove", "origin"], cwd=self.repo_path, check=False, timeout=10) 
            return True
        except subprocess.TimeoutExpired as e:
            print(f"{Emojis.CLOCK.value} Command timed out: {e}")
            return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to remove upstream: {e}")
            return False
        
    def add_upstream(self) -> bool:
        """
        Adds the upstream remote to the specified repository path.

        Args:
            repo_path (str): The path to the repository.
            repo_url (str): The URL of the repository to add as the upstream remote. repo = f"https://{user_login}:{self.gh_token}@github.com/{user_login}/{repo_name}.git"
        Returns:
            bool: True if the upstream remote was successfully added, False otherwise.
        """
        try:
            subprocess.run(["git", "remote", "add", "origin", self.remote_url], cwd=self.repo_path, timeout=10)
            return True
        except subprocess.TimeoutExpired as e:
            print(f"{Emojis.CLOCK.value} Command timed out: {e}")
            return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to add upstream: {e}")
            return
        
    
    def add_commit_push(self, branchname: str = "main") -> bool:
        """
        Pushes the local repository to the remote repository.

        Args:
            repo_path (str): The path to the local repository.
            repo_name (str): The name of the remote repository to be created.
        Returns:
            bool: True if the repository was successfully pushed, False otherwise.
        """
        try:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, timeout=10)
            subprocess.run(["git", "commit", "-m", "saasFactory - Initial commit"], cwd=self.repo_path, timeout=10)
            subprocess.run(["git", "branch", "-M", branchname], cwd=self.repo_path, timeout=10)
            subprocess.run(["git", "push", "-u", "origin", branchname], cwd=self.repo_path, timeout=10)
            return True
        except subprocess.TimeoutExpired as e:
            print(f"{Emojis.CLOCK.value} Command timed out: {e}")
            return False
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to push to repository: {e}")
            return False

    def add_deploy_keys(self, key_title: str, key: str) -> bool:
        """
        Adds a deploy key to the remote GitHub repository.
        Args:
            key_title (str): The title of the deploy key.
            key (str): The deploy key to add.   
        Returns:
            bool: True if the deploy key was successfully added, False otherwise.
        """
        try:
            self.new_repo.create_key(key_title, key)
            return True
        except Exception as e:
            print(f"{Emojis.ERROR_SIGN.value} Failed to add deploy key: {e}")
            return False

        