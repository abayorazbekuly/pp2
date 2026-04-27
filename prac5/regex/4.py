import re

s = input()
print(re.findall(r"\b[A-Z][a-z]+\b", s))