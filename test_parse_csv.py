import re
with open('subscriptions.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

less_than_7 = 0
total = 0
for line in lines[1:]:
    line = line.strip()
    if not line: continue
    total += 1
    parts = re.split(r'\s{2,}', line)
    if len(parts) < 7:
        less_than_7 += 1

print(f"Total: {total}, Less than 7: {less_than_7}")
