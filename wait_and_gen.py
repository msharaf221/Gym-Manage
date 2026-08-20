import time
import sqlite3
import subprocess

print("Waiting for import to finish...")
while True:
    try:
        conn = sqlite3.connect('gym.db', timeout=1)
        # Check if import is still running by checking DB lock
        conn.execute("BEGIN IMMEDIATE")
        conn.rollback()
        conn.close()
        break
    except sqlite3.OperationalError:
        time.sleep(2)

print("DB is free. Regenerating tickets...")
subprocess.run("source venv/bin/activate && python3 -c 'import app; app.init_db(); from utils import regenerate_all_tickets; regenerate_all_tickets()'", shell=True)
print("Done!")
