import shutil
import os

os.makedirs("dest", exist_ok=True)

shutil.copy("sample.txt", "dest/sample.txt")