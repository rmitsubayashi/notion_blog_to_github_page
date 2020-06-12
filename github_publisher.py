from git import Repo

class GithubPublisher:
    def __init__(self, remote_repo_path):
        self._remote_repo_path = remote_repo_path
    
    def publish(self, local_path, staged_files, unstaged_files):
        # assumes github repo converter created a git repository
        repo = Repo(local_path)

        assert len(repo.remotes) > 0
            
        repo.remotes['origin'].pull()
        
        repo.index.add(staged_files)
        # need empty checking or crashes :(
        if len(unstaged_files) > 0:
            repo.index.remove(unstaged_files)
        repo.index.commit("update blog")
        
        repo.remotes['origin'].push()
        
        return True