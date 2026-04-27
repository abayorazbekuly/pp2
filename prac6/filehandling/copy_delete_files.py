# copy_delete_files.py

import shutil
import os

# copy file
shutil.copy("sample.txt", "sample_backup.txt")

# delete backup file
if os.path.exists("sample_backup.txt"):
    os.remove("sample_backup.txt")