# write_files.py

with open("sample.txt", "w") as f:
    f.write("Hello\n")
    f.write("Python File Handling\n")

with open("sample.txt", "a") as f:
    f.write("New line added\n")