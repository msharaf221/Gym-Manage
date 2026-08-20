import sys

with open("app.py", "r") as f:
    content = f.read()

new_route = """@app.route('/withdrawals/empty_wallet', methods=['POST'])
@login_required
@permission('can_withdrawals')
def empty_wallet():
    conn = get_connection()
    wallet_in = conn.execute("SELECT COALESCE(SUM(amount), 0) s FROM cash_flow WHERE payment_method='wallet' AND direction='in'").fetchone()['s']
    wallet_out = conn.execute("SELECT COALESCE(SUM(amount), 0) s FROM cash_flow WHERE payment_method='wallet' AND direction='out'").fetchone()['s']
    balance = wallet_in - wallet_out
    
    if balance > 0:
        cur = conn.execute(
            "INSERT INTO withdrawals (amount, reason, withdrawal_date, business_date, business_month, "
            "created_by) VALUES (?,?,?,?,?,?)",
            (balance, 'سحب وتصفير المحفظة', business_date().isoformat(), business_date().isoformat(),
             business_month(), session['user_id']))
        wid = cur.lastrowid
        conn.commit()
        record_cash_flow('withdrawal', 'withdrawals', wid, 'out', balance, 'سحب وتصفير المحفظة',
                         'wallet', session['user_id'])
        log_audit(session['user_id'], 'empty_wallet', 'withdrawal', wid)
        flash(f'تم تصفير المحفظة وسحب مبلغ {balance} بنجاح.', 'success')
    else:
        flash('المحفظة فارغة بالفعل.', 'info')
        
    conn.close()
    return redirect(url_for('withdrawals'))

@app.route('/withdrawal/<int:wid>/delete', methods=['POST'])
@login_required
@permission('can_delete_withdrawals')
def delete_withdrawal(wid):"""

old_str = """@app.route('/withdrawal/<int:wid>/delete', methods=['POST'])
@login_required
@permission('can_delete_withdrawals')
def delete_withdrawal(wid):"""

if old_str in content:
    content = content.replace(old_str, new_route)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
