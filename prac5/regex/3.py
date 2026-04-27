import re

s = input()
print(re.findall(r"\b[a-z]+_[a-z]+\b", s))