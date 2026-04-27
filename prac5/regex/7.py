s = input().strip()

parts = s.split("_")
camel = parts[0].lower() + "".join(p.capitalize() for p in parts[1:] if p)
print(camel)