import re

s = input().strip()
print(re.split(r"(?<!^)(?=[A-Z])", s))