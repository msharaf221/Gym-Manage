import sys

with open("app.py", "r") as f:
    content = f.read()

new_route = """@app.route('/salaries/delete/<int:emp_id>', methods=['POST'])
@login_required
@permission('can_staff')
def delete_employee(emp_id):
    conn = get_connection()
    # Find loans and salaries to delete from cash_flow
    loans = conn.execute("SELECT loan_id FROM loans WHERE emp_id = ?", (emp_id,)).fetchall()
    salaries = conn.execute("SELECT payment_id FROM salary_payments WHERE emp_id = ?", (emp_id,)).fetchall()
    
    for l in loans:
        conn.execute("DELETE FROM cash_flow WHERE source_table = 'loans' AND source_id = ?", (l['loan_id'],))
    for s in salaries:
        conn.execute("DELETE FROM cash_flow WHERE source_table = 'salary_payments' AND source_id = ?", (s['payment_id'],))
        
    conn.execute("DELETE FROM loans WHERE emp_id = ?", (emp_id,))
    conn.execute("DELETE FROM salary_payments WHERE emp_id = ?", (emp_id,))
    conn.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()
    log_audit(session['user_id'], 'delete_employee', 'employee', emp_id, request=request)
    flash('تم حذف الموظف نهائياً.', 'success')
    return redirect(url_for('salaries'))"""

old_str = """@app.route('/salaries/delete/<int:emp_id>', methods=['POST'])
@login_required
@permission('can_staff')
def delete_employee(emp_id):
    conn = get_connection()
    conn.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()
    log_audit(session['user_id'], 'delete_employee', 'employee', emp_id, request=request)
    flash('تم حذف الموظف نهائياً.', 'success')
    return redirect(url_for('salaries'))"""

if old_str in content:
    content = content.replace(old_str, new_route)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
