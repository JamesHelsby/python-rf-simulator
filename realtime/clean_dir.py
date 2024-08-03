import glob
import shutil


def clean_temp_dirs(pattern="/tmp/tmp.*"):
    for temp_dir in glob.glob(pattern):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error removing {temp_dir}: {e}")
