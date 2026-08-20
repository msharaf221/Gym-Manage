import openpyxl
wb = openpyxl.load_workbook('subscriptions.xlsx', data_only=True, read_only=True)
c = 0
for r in wb.active.iter_rows(min_row=2, values_only=True):
    if not r[0] and r[1]:
        print(r)
        c += 1
        if c >= 10: break
