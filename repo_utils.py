import os
import shutil
from git import Repo

def clone_repo(url, target_dir):
    """
    Clones a repo from url into target_dir
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    Repo.clone_from(url, target_dir)
    return target_dir
