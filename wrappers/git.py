from git.repo.base import Repo


class GIT:
    @classmethod
    def clone(cls, url, path):
        Repo.clone_from(url, path)
