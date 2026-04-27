import re

s = input().strip()
print(re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower())