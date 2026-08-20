import sys

with open("app.py", "r") as f:
    content = f.read()

new_str = """    total_in = cash_in + wallet_in
    total_out = cash_out + wallet_out
    net = total_in - total_out
    
    # Fetch detailed transactions
    transactions = conn.execute('''
        SELECT c.*, u.full_name as user_name
        FROM cash_flow c
        LEFT JOIN users u ON c.created_by = u.id
        WHERE c.business_date = ?
        ORDER BY c.flow_id DESC
    ''', (date_str,)).fetchall()
    
    conn.close()

    report = dict(
        date=date_str,
        rep=rep,
        cash_in=cash_in, wallet_in=wallet_in,
        cash_out=cash_out, wallet_out=wallet_out,
        cash_net=cash_in - cash_out,
        wallet_net=wallet_in - wallet_out,
        total_in=total_in, total_out=total_out, net=net,
        checkins=checkins,
        transactions=transactions
    )
    return render_template('daily_report.html', report=report)"""

old_str = """    total_in = cash_in + wallet_in
    total_out = cash_out + wallet_out
    net = total_in - total_out
    conn.close()

    report = dict(
        date=date_str,
        rep=rep,
        cash_in=cash_in, wallet_in=wallet_in,
        cash_out=cash_out, wallet_out=wallet_out,
        cash_net=cash_in - cash_out,
        wallet_net=wallet_in - wallet_out,
        total_in=total_in, total_out=total_out, net=net,
        checkins=checkins
    )
    return render_template('daily_report.html', report=report)"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
