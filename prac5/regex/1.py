import re

s = input().strip()
print(bool(re.fullmatch(r"ab*", s)))