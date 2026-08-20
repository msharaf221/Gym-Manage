import sys

with open("app.py", "r") as f:
    content = f.read()

new_route = """def mark_read(nid):
    conn = get_connection()
    conn.execute("UPDATE notifications SET is_read = 1 WHERE notif_id = ? AND user_id = ?",
                 (nid, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    conn = get_connection()
    conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?",
                 (session['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True})"""

old_str = """def mark_read(nid):
    conn = get_connection()
    conn.execute("UPDATE notifications SET is_read = 1 WHERE notif_id = ? AND user_id = ?",
                 (nid, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})"""

if old_str in content:
    content = content.replace(old_str, new_route)
    with open("app.py", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
