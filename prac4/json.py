import json
from pathlib import Path

FILE = Path(__file__).with_name("sample-data.json")

def cut(s: str, w: int) -> str:
    s = s or ""
    return s if len(s) <= w else s[: w - 3] + "..."

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

imdata = data.get("imdata", [])

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<8} {'MTU':<6}")
print(f"{'-'*50} {'-'*20} {'-'*6} {'-'*6}")

for item in imdata:
    obj = item.get("l1PhysIf")
    if not obj:
        continue
    a = obj.get("attributes", {})
    dn = a.get("dn", "")
    descr = cut(a.get("descr", ""), 20)
    speed = a.get("speed", "")
    mtu = a.get("mtu", "")
    print(f"{cut(dn, 50):<50} {descr:<20} {cut(speed, 8):<8} {cut(mtu, 6):<6}")