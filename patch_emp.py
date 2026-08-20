import sys

with open("app.py", "r") as f:
    content = f.read()

new_route = """@app.route('/employee/<int:emp_id>/delete', methods=['POST'])
@login_required
@permission('can_staff')
def delete_employee(emp_id):
    conn = get_connection()
    conn.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()
    log_audit(session['user_id'], 'delete_employee', 'employee', emp_id, request=request)
    flash('تم حذف الموظف نهائياً.', 'success')
    return redirect(url_for('salaries'))

@app.route('/employee/<int:emp_id>/archive', methods=['POST'])
@login_required
@permission('can_staff')
def archive_employee(emp_id):"""

old_str = """@app.route('/employee/<int:emp_id>/archive', methods=['POST'])
@login_required
@permission('can_staff')
def archive_employee(emp_id):"""

if old_str in content:
    content = content.replace(old_str, new_route)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
