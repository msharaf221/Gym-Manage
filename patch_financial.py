import sys

with open("app.py", "r") as f:
    content = f.read()

new_str = """@permission('can_monthly_reports')
def financial_reports():
    conn = get_connection()
    # Last 6 business months
    months = []
    bm = business_month()
    y, m = map(int, bm.split('-'))
    for i in range(6):
        mo = m - i
        yy = y
        while mo <= 0:
            mo += 12
            yy -= 1
        label = f'{yy:04d}-{mo:02d}'
        
        # Breakdown
        rows = conn.execute(
            "SELECT flow_type, direction, payment_method, SUM(amount) as s "
            "FROM cash_flow WHERE business_month=? GROUP BY flow_type, direction, payment_method",
            (label,)
        ).fetchall()
        
        rep = {
            'sub_cash': 0, 'sub_wallet': 0,
            'sale_cash': 0, 'sale_wallet': 0,
            'session_cash': 0, 'session_wallet': 0,
            'loan_repay_cash': 0, 'loan_repay_wallet': 0,
            'withdrawals_cash': 0, 'withdrawals_wallet': 0,
            'loans_given_cash': 0, 'loans_given_wallet': 0
        }
        for r in rows:
            ft = r['flow_type']
            pm = r['payment_method'] or 'cash'
            val = r['s'] or 0
            if ft == 'subscription' and r['direction'] == 'in': rep[f'sub_{pm}'] += val
            if ft == 'sale' and r['direction'] == 'in': rep[f'sale_{pm}'] += val
            if ft == 'session' and r['direction'] == 'in': rep[f'session_{pm}'] += val
            if ft == 'loan_repayment' and r['direction'] == 'in': rep[f'loan_repay_{pm}'] += val
            if ft == 'withdrawal' and r['direction'] == 'out': rep[f'withdrawals_{pm}'] += val
            if ft == 'loan_given' and r['direction'] == 'out': rep[f'loans_given_{pm}'] += val
            
        cash_in = rep['sub_cash'] + rep['sale_cash'] + rep['session_cash'] + rep['loan_repay_cash']
        wallet_in = rep['sub_wallet'] + rep['sale_wallet'] + rep['session_wallet'] + rep['loan_repay_wallet']
        cash_out = rep['withdrawals_cash'] + rep['loans_given_cash']
        wallet_out = rep['withdrawals_wallet'] + rep['loans_given_wallet']
        
        months.append({
            'label': label,
            'in': cash_in + wallet_in,
            'out': cash_out + wallet_out,
            'net': (cash_in + wallet_in) - (cash_out + wallet_out),
            'cash_in': cash_in, 'wallet_in': wallet_in,
            'cash_out': cash_out, 'wallet_out': wallet_out,
            'cash_net': cash_in - cash_out,
            'wallet_net': wallet_in - wallet_out,
            'rep': rep
        })
    snapshots = conn.execute("SELECT * FROM monthly_snapshots ORDER BY snapshot_id DESC").fetchall()
    conn.close()
    return render_template('financial_reports.html', months=months, snapshots=snapshots)"""

old_str = """@permission('can_monthly_reports')
def financial_reports():
    conn = get_connection()
    # Last 6 business months
    months = []
    bm = business_month()
    y, m = map(int, bm.split('-'))
    for i in range(6):
        mo = m - i
        yy = y
        while mo <= 0:
            mo += 12
            yy -= 1
        label = f'{yy:04d}-{mo:02d}'
        row = conn.execute(
            "SELECT "
            "COALESCE(SUM(CASE WHEN direction='in' THEN amount END),0) AS in_amt, "
            "COALESCE(SUM(CASE WHEN direction='out' THEN amount END),0) AS out_amt "
            "FROM cash_flow WHERE business_month = ?", (label,)).fetchone()
        months.append({'label': label, 'in': row['in_amt'], 'out': row['out_amt'],
                       'net': row['in_amt'] - row['out_amt']})
    snapshots = conn.execute("SELECT * FROM monthly_snapshots ORDER BY snapshot_id DESC").fetchall()
    conn.close()
    return render_template('financial_reports.html', months=months, snapshots=snapshots)"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
