import openpyxl
wb = openpyxl.load_workbook('subscriptions.xlsx', data_only=True, read_only=True)
sheet = wb.active

skipped_no_id = 0
skipped_bad_id = 0
skipped_no_name = 0

for row in sheet.iter_rows(min_row=2, values_only=True):
    if not row or not row[0]: 
        skipped_no_id += 1
        continue
    
    try:
        m_id = int(row[0])
    except:
        skipped_bad_id += 1
        continue
        
    name = str(row[1] or '').strip()
    if not name: 
        skipped_no_name += 1
        continue

print(f"Skipped NO ID: {skipped_no_id}")
print(f"Skipped BAD ID: {skipped_bad_id}")
print(f"Skipped NO NAME: {skipped_no_name}")
