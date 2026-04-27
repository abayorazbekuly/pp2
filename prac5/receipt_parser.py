import re
import json

def money(s: str) -> float:
    return float(s.replace(" ", "").replace(",", "."))

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read().replace("\r\n", "\n").replace("\r", "\n") #открываем файл и читаем

m = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})", text)
date, time = (m.group(1), m.group(2)) if m else (None, None)

payment_method = "Банковская карта" if "Банковская карта" in text else None

m = re.search(r"ИТОГО:\s*([0-9 ]+,\d{2})", text) #итоги 
total = money(m.group(1)) if m else None

item_pat = re.compile(
    r"(?ms)^\s*(\d+)\.\s*\n"          #номер
    r"(.+?)\n"                       #название
    r"(\d+,\d{3})\s*x\s*([0-9 ]+,\d{2})\n"  #qty x unit
    r"([0-9 ]+,\d{2})\n"             #line_total
)

items = []
for idx, name, qty, unit, line_total in item_pat.findall(text):
    items.append({
        "index": int(idx),
        "name": re.sub(r"\s{2,}", " ", name.strip()),
        "qty": float(qty.replace(",", ".")),
        "unit_price": money(unit),
        "line_total": money(line_total),
    })

calc_total = round(sum(i["line_total"] for i in items), 2)
#all_prices = [money(x) for x in re.findall(r"\b([0-9 ]+,\d{2})\b", text)]

result = {
    "datetime": {"date": date, "time": time},
    "payment_method": payment_method,
    "items": items,
    "items_count": len(items),
    "total_found": total,
    "total_calculated": calc_total,
    #"all_prices_found": all_prices,
}

print(json.dumps(result, ensure_ascii=False, indent=2))