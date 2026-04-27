from datetime import datetime, timedelta

# 1) subtract five days from current date
print((datetime.now() - timedelta(days=5)).date())

# 2) yesterday, today, tomorrow
today = datetime.now().date()
print(today - timedelta(days=1))
print(today)
print(today + timedelta(days=1))

# 3) drop microseconds from datetime
print(datetime.now().replace(microsecond=0))

# 4) difference between two dates in seconds (input: YYYY-MM-DD HH:MM:SS)
d1 = datetime.strptime(input().strip(), "%Y-%m-%d %H:%M:%S")
d2 = datetime.strptime(input().strip(), "%Y-%m-%d %H:%M:%S")
print(int((d2 - d1).total_seconds()))