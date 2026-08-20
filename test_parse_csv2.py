import re
with open('subscriptions.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

count = 0
for line in lines[1:]:
    line = line.strip()
    if not line: continue
    parts = re.split(r'\s{2,}', line)
    if len(parts) < 7:
        print(parts)
        count += 1
        if count >= 10: break
