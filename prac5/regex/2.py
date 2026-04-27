import re

s = input().strip()
print(bool(re.fullmatch(r"ab{2,3}", s)))