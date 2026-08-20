import sqlite3
from datetime import datetime
import openpyxl

conn = sqlite3.connect('gym.db')

print("Clearing old member data...")
conn.execute("DELETE FROM members")
conn.execute("DELETE FROM subscriptions")
conn.execute("DELETE FROM attendance")
conn.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name IN ('members', 'subscriptions', 'attendance')")
conn.commit()

print("Reading subscriptions.xlsx...")
wb = openpyxl.load_workbook('subscriptions.xlsx', data_only=True, read_only=True)
sheet = wb.active

member_ids_seen = set()
count = 0

for row in sheet.iter_rows(min_row=2, values_only=True):
    if not row or not row[0]: continue
    
    try:
        m_id = int(row[0])
    except:
        continue
        
    name = str(row[1] or '').strip()
    if not name: continue
    
    start_date = None
    if row[2]:
        if isinstance(row[2], datetime):
            start_date = row[2].strftime("%Y-%m-%d")
        else:
            try:
                start_date = datetime.strptime(str(row[2]).strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                start_date = str(row[2]).strip()
                
    end_date = None
    if row[3]:
        if isinstance(row[3], datetime):
            end_date = row[3].strftime("%Y-%m-%d")
        else:
            try:
                end_date = datetime.strptime(str(row[3]).strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                end_date = str(row[3]).strip()
                
    phone = str(row[4] or '').strip()
    if phone == '0': phone = ''
    
    plan_type = str(row[5] or '').strip()
    
    try:
        paid = float(str(row[6]).replace(',', '')) if row[6] is not None else 0.0
    except:
        paid = 0.0
        
    try:
        debt = float(str(row[7]).replace(',', '')) if len(row) > 7 and row[7] is not None else 0.0
    except:
        debt = 0.0
        
    price = paid + debt
    
    status = 'active'
    if end_date:
        try:
            if datetime.strptime(end_date, "%Y-%m-%d") < datetime.now():
                status = 'expired'
        except:
            pass
            
    if m_id not in member_ids_seen:
        conn.execute("INSERT INTO members (id, full_name, phone, created_by, created_at, status) VALUES (?,?,?,?,?,?)",
                     (m_id, name, phone, 1, start_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status))
        member_ids_seen.add(m_id)
        
    conn.execute("INSERT INTO subscriptions (member_id, plan_type, price, amount_paid, start_date, end_date, is_paid, created_by, business_date, business_month) VALUES (?,?,?,?,?,?,?,?,?,?)",
                 (m_id, plan_type, price, paid, start_date, end_date, 1 if debt <= 0 else 0, 1, start_date, start_date[:7] if start_date and len(start_date)>=7 else None))
    
    count += 1
    if count % 1000 == 0:
        conn.commit()
        print(f"Imported {count}...")

conn.commit()
conn.close()
print(f"Done! Total imported: {count}")
