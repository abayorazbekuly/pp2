import os

os.makedirs("test_dir/sub_dir", exist_ok=True)

print("Current directory:", os.getcwd())

files = os.listdir(".")
print("Files:", files)