import sys

with open("app.py", "r") as f:
    content = f.read()

old_str = """    checkins = conn.execute(
        "SELECT COUNT(*) c FROM attendance WHERE business_date=?", (date_str,)).fetchone()['c']

    total_in = sub_cash + sale_cash + session_cash + loan_repay
    total_out = withdrawals_total + loans_given
    net = total_in - total_out
    conn.close()

    report = dict(
        date=date_str,
        sub_cash=sub_cash, sale_cash=sale_cash, session_cash=session_cash,
        loan_repay=loan_repay, loans_given=loans_given, withdrawals=withdrawals_total,
        total_in=total_in, total_out=total_out, net=net, checkins=checkins)
    return render_template('daily_report.html', report=report)"""

new_str = """    checkins = conn.execute(
        "SELECT COUNT(*) c FROM attendance WHERE business_date=?", (date_str,)).fetchone()['c']

    cash_in = rep['sub_cash'] + rep['sale_cash'] + rep['session_cash'] + rep['loan_repay_cash']
    wallet_in = rep['sub_wallet'] + rep['sale_wallet'] + rep['session_wallet'] + rep['loan_repay_wallet']
    cash_out = rep['withdrawals_cash'] + rep['loans_given_cash']
    wallet_out = rep['withdrawals_wallet'] + rep['loans_given_wallet']
    
    total_in = cash_in + wallet_in
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
