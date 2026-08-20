import csv, re, sqlite3
from datetime import datetime

with open('subscriptions.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

parsed = []
for line in lines[1:]: # skip header
    line = line.strip()
    if not line: continue
    parts = re.split(r'\s{2,}', line)
    parsed.append(parts)

print("Total parsed lines:", len(parsed))
for i in range(5):
    print(parsed[i])
