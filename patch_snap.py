import sys

with open("app.py", "r") as f:
    content = f.read()

new_str = """def create_snapshot():
    conn = get_connection()
    bm = business_month()
    start, end = business_month_bounds(bm)
    
    # Calculate everything from cash_flow as the single source of truth
    row = conn.execute(
        "SELECT "
        "COALESCE(SUM(CASE WHEN direction='in' THEN amount END),0) in_amt, "
        "COALESCE(SUM(CASE WHEN direction='out' THEN amount END),0) out_amt, "
        "COALESCE(SUM(CASE WHEN flow_type='subscription' THEN amount END),0) sub_amt, "
        "COALESCE(SUM(CASE WHEN flow_type='sale' THEN amount END),0) sale_amt, "
        "COALESCE(SUM(CASE WHEN flow_type='withdrawal' THEN amount END),0) with_amt "
        "FROM cash_flow WHERE business_month = ?", (bm,)).fetchone()
        
    payments = row['sub_amt']
    sales_total = row['sale_amt']
    withdrawals_total = row['with_amt']
    member_count = conn.execute("SELECT COUNT(*) c FROM members").fetchone()['c']

    # Upsert snapshot
    conn.execute(
        "INSERT INTO monthly_snapshots (year_month, start_date, end_date, total_payments, total_sales, "
        "total_withdrawals, net_revenue, member_count, created_by) VALUES (?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(year_month) DO UPDATE SET total_payments=excluded.total_payments, "
        "total_sales=excluded.total_sales, total_withdrawals=excluded.total_withdrawals, "
        "net_revenue=excluded.net_revenue, member_count=excluded.member_count",
        (bm, start.isoformat(), end.isoformat(), payments, sales_total, withdrawals_total,
         row['in_amt'] - row['out_amt'], member_count, session['user_id']))
    conn.commit()"""

old_str = """def create_snapshot():
    conn = get_connection()
    bm = business_month()
    start, end = business_month_bounds(bm)
    row = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN direction='in' THEN amount END),0) in_amt, "
        "COALESCE(SUM(CASE WHEN direction='out' THEN amount END),0) out_amt "
        "FROM cash_flow WHERE business_month = ?", (bm,)).fetchone()
    payments = conn.execute(
        "SELECT COALESCE(SUM(amount_paid),0) s FROM subscriptions WHERE business_month = ?", (bm,)).fetchone()['s']
    sales_total = conn.execute(
        "SELECT COALESCE(SUM(total),0) s FROM sales WHERE business_month = ?", (bm,)).fetchone()['s']
    withdrawals_total = conn.execute(
        "SELECT COALESCE(SUM(amount),0) s FROM withdrawals WHERE business_month = ?", (bm,)).fetchone()['s']
    member_count = conn.execute("SELECT COUNT(*) c FROM members").fetchone()['c']

    # Upsert snapshot
    conn.execute(
        "INSERT INTO monthly_snapshots (year_month, start_date, end_date, total_payments, total_sales, "
        "total_withdrawals, net_revenue, member_count, created_by) VALUES (?,?,?,?,?,?,?,?,?) "
        "ON CONFLICT(year_month) DO UPDATE SET total_payments=excluded.total_payments, "
        "total_sales=excluded.total_sales, total_withdrawals=excluded.total_withdrawals, "
        "net_revenue=excluded.net_revenue, member_count=excluded.member_count",
        (bm, start.isoformat(), end.isoformat(), payments, sales_total, withdrawals_total,
         row['in_amt'] - row['out_amt'], member_count, session['user_id']))
    conn.commit()"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
