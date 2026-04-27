import re

s = input().strip()
print(bool(re.fullmatch(r"a.*b", s)))