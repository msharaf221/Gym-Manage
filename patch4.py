import sys

with open("templates/base.html", "r") as f:
    content = f.read()

new_script = """
    function markAllRead(e) {
      if (e) { e.preventDefault(); e.stopPropagation(); }
      fetch('/api/notifications/mark-all-read' + (AUTH_TOKEN ? '?token=' + encodeURIComponent(AUTH_TOKEN) : ''), { method: 'POST' })
        .then(() => {
           document.querySelectorAll('.badge.bg-danger').forEach(b => b.remove());
           document.querySelectorAll('#notif-list .bg-light').forEach(el => el.classList.remove('bg-light'));
        });
    }

    fetch('/api/notifications' + (AUTH_TOKEN ? '?token=' + encodeURIComponent(AUTH_TOKEN) : ''))
"""

old_str = """
    fetch('/api/notifications' + (AUTH_TOKEN ? '?token=' + encodeURIComponent(AUTH_TOKEN) : ''))
"""

if old_str in content:
    content = content.replace(old_str, new_script)
    with open("templates/base.html", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("String not found!")
