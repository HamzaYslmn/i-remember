import os
import shutil
import sys

def find_and_remove_pycache_and_pyc(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # remove __pycache__ dirs
        list(
            map(
                lambda d: remove_pycache(os.path.join(dirpath, d)),
                filter(lambda d: d == '__pycache__', dirnames)
            )
        )
        # remove .pyc files
        list(
            map(
                lambda f: remove_pyc_file(os.path.join(dirpath, f)),
                filter(lambda f: f.endswith('.pyc'), filenames)
            )
        )

def remove_pycache(path):
    try:
        shutil.rmtree(path)
        print(f"Removed directory: {path}")
    except Exception as e:
        print(f"Error removing directory {path}: {e}")

def remove_pyc_file(path):
    try:
        os.remove(path)
        print(f"Removed file: {path}")
    except Exception as e:
        print(f"Error removing file {path}: {e}")

if __name__ == "__main__":
    # start from this script's directory or first CLI arg
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.dirname(__file__))
    find_and_remove_pycache_and_pyc(root)