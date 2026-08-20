import sqlite3, re
from datetime import datetime

conn = sqlite3.connect('gym.db')

print("Clearing old member data...")
conn.execute("DELETE FROM members")
conn.execute("DELETE FROM subscriptions")
conn.execute("DELETE FROM attendance")
conn.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name IN ('members', 'subscriptions', 'attendance')")

print("Reading subscriptions.csv...")
with open('subscriptions.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def parse_date(d_str):
    if not d_str or d_str == '0': return None
    # sometimes date is 2024 instead of 2024-01-01?
    try:
        return datetime.strptime(d_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception:
        try:
            return datetime.strptime(d_str, "%m/%d/%Y").strftime("%Y-%m-%d")
        except:
            return d_str # fallback to literal string if unparseable

member_ids_seen = set()

count = 0
for line in lines[1:]:
    line = line.strip()
    if not line: continue
    parts = re.split(r'\s{2,}', line)
    
    if len(parts) < 7:
        continue
        
    try:
        m_id = int(parts[0])
    except ValueError:
        continue # skip rows like "الاربع"
        
    name = parts[1]
    start_date = parse_date(parts[2])
    end_date = parse_date(parts[3])
    phone = parts[4] if parts[4] != '0' else ''
    plan_type = parts[5]
    try:
        paid = float(parts[6].replace(',', ''))
    except:
        paid = 0.0
        
    debt = 0.0
    if len(parts) > 7:
        try:
            debt = float(parts[7].replace(',', ''))
        except:
            pass
            
    price = paid + debt
    
    status = 'active'
    if end_date:
        try:
            if datetime.strptime(end_date, "%Y-%m-%d") < datetime.now():
                status = 'expired'
        except:
            pass
    
    # Insert member if not exists
    if m_id not in member_ids_seen:
        conn.execute("INSERT INTO members (id, full_name, phone, created_by, created_at, status) VALUES (?,?,?,?,?,?)",
                     (m_id, name, phone, 1, start_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status))
        member_ids_seen.add(m_id)
        
    # Insert subscription
    conn.execute("INSERT INTO subscriptions (member_id, plan_type, price, amount_paid, start_date, end_date, is_paid, created_by, business_date, business_month) VALUES (?,?,?,?,?,?,?,?,?,?)",
                 (m_id, plan_type, price, paid, start_date, end_date, 1 if debt <= 0 else 0, 1, start_date, start_date[:7] if start_date and len(start_date)>=7 else None))
    count += 1

conn.commit()
conn.close()
print(f"Imported {count} subscriptions/members successfully!")
