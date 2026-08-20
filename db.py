"""
Power Home Gym Management System - Database Layer
SQLite schema initialization and connection helpers.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'gym.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
BARCODE_DIR = os.path.join(BASE_DIR, 'static', 'barcodes')


def ensure_dirs():
    for d in (UPLOAD_DIR, BARCODE_DIR):
        os.makedirs(d, exist_ok=True)


def get_connection():
    """Open a new SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'staff',
    is_active INTEGER DEFAULT 1,
    can_add_members INTEGER DEFAULT 1,
    can_view_members INTEGER DEFAULT 1,
    can_edit_members INTEGER DEFAULT 0,
    can_delete_members INTEGER DEFAULT 0,
    can_checkin INTEGER DEFAULT 1,
    can_sales INTEGER DEFAULT 1,
    can_delete_sales INTEGER DEFAULT 0,
    can_view_finance INTEGER DEFAULT 0,
    can_withdrawals INTEGER DEFAULT 0,
    can_delete_withdrawals INTEGER DEFAULT 0,
    can_delete_sessions INTEGER DEFAULT 0,
    can_daily_reports INTEGER DEFAULT 0,
    can_monthly_reports INTEGER DEFAULT 0,
    can_export INTEGER DEFAULT 0,
    can_backup INTEGER DEFAULT 0,
    can_products INTEGER DEFAULT 0,
    can_sessions INTEGER DEFAULT 0,
    can_staff INTEGER DEFAULT 0,
    can_whatsapp INTEGER DEFAULT 0,
    can_manage_users INTEGER DEFAULT 0,
    can_settings INTEGER DEFAULT 0,
    can_audit INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    photo_path TEXT,
    qr_code_path TEXT,
    barcode_path TEXT,
    status TEXT DEFAULT 'active',
    gender TEXT,
    whatsapp TEXT,
    description TEXT,
    notes TEXT,
    freeze_start TEXT,
    frozen_days INTEGER DEFAULT 0,
    is_frozen INTEGER DEFAULT 0,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS subscriptions (
    sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    plan_type TEXT,
    price REAL DEFAULT 0,
    amount_paid REAL DEFAULT 0,
    start_date TEXT,
    end_date TEXT,
    is_paid INTEGER DEFAULT 0,
    payment_date TEXT,
    business_date TEXT,
    business_month TEXT,
    created_by INTEGER,
    whatsapp_sent INTEGER DEFAULT 0,
    payment_method TEXT DEFAULT 'cash',
    FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS attendance (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    check_in_time TEXT DEFAULT (datetime('now', 'localtime')),
    business_date TEXT,
    logged_by INTEGER,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    photo_path TEXT,
    barcode_path TEXT,
    stock_quantity INTEGER DEFAULT 0,
    price REAL DEFAULT 0,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    product_id INTEGER,
    quantity INTEGER DEFAULT 1,
    price REAL DEFAULT 0,
    total REAL DEFAULT 0,
    sale_date TEXT,
    business_date TEXT,
    business_month TEXT,
    created_by INTEGER,
    notes TEXT,
    payment_method TEXT DEFAULT 'cash'
);

CREATE TABLE IF NOT EXISTS daily_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    member_name TEXT,
    phone TEXT,
    price REAL DEFAULT 0,
    sessions_count INTEGER DEFAULT 1,
    sessions_used INTEGER DEFAULT 0,
    session_date TEXT,
    business_date TEXT,
    payment_method TEXT DEFAULT 'cash',
    notes TEXT,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS withdrawals (
    withdrawal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL DEFAULT 0,
    reason TEXT,
    withdrawal_date TEXT,
    business_date TEXT,
    business_month TEXT,
    created_by INTEGER
);

CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    job_title TEXT,
    salary REAL DEFAULT 0,
    basic_salary REAL DEFAULT 0,
    total_advances REAL DEFAULT 0,
    net_due REAL DEFAULT 0,
    last_salary_payment_date TEXT,
    is_active INTEGER DEFAULT 1,
    archived_at TEXT,
    archived_by INTEGER,
    hire_date TEXT,
    notes TEXT,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    amount REAL DEFAULT 0,
    reason TEXT,
    loan_date TEXT,
    business_date TEXT,
    is_repaid INTEGER DEFAULT 0,
    repaid_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_by INTEGER,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

CREATE TABLE IF NOT EXISTS salary_payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    basic_salary REAL DEFAULT 0,
    total_advances REAL DEFAULT 0,
    net_paid REAL DEFAULT 0,
    payment_date TEXT,
    business_date TEXT,
    business_month TEXT,
    notes TEXT,
    created_by INTEGER,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

CREATE TABLE IF NOT EXISTS cash_flow (
    flow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_type TEXT,
    source_table TEXT,
    source_id INTEGER,
    direction TEXT,
    amount REAL DEFAULT 0,
    reason TEXT,
    business_date TEXT,
    business_month TEXT,
    payment_method TEXT DEFAULT 'cash',
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    meta_json TEXT
);

CREATE TABLE IF NOT EXISTS monthly_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_month TEXT UNIQUE,
    start_date TEXT,
    end_date TEXT,
    total_payments REAL DEFAULT 0,
    total_sales REAL DEFAULT 0,
    total_withdrawals REAL DEFAULT 0,
    net_revenue REAL DEFAULT 0,
    member_count INTEGER DEFAULT 0,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS notifications (
    notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    message TEXT,
    notif_type TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS whatsapp_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    phone TEXT,
    message TEXT,
    msg_type TEXT,
    status TEXT DEFAULT 'pending',
    sent_at TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    entity_type TEXT,
    entity_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TEXT DEFAULT (datetime('now', 'localtime'))
);
"""


DEFAULT_SETTINGS = {
    'gym_name': 'Power Home',
    'primary_color': '#2563EB',
    'accent_color': '#F3F4F6',
    'day_start_hour': '4',
    'month_start_day': '25',
    'whatsapp_enabled': '1',
    'whatsapp_token': '',
    'whatsapp_phone_id': '',
    'currency': 'EGP',
    'welcome_template': 'أهلاً {member_name} في {gym_name}! اشتراكك ساري حتى {expiry_date}.',
    'reminder_template': 'عزيزي {member_name}، اشتراكك في {gym_name} ينتهي بتاريخ {expiry_date} (متبقي {days_left} يوم).',
    'debt_template': 'عزيزي {member_name}، لديك مبلغ متبقي قدره {remaining_amount} في {gym_name}.',
    'freeze_template': 'عزيزي {member_name}، تم تجميد اشتراكك في {gym_name} حتى إشعار آخر.',
    'unfreeze_template': 'عزيزي {member_name}، اشتراكك في {gym_name} نشط الآن مجدداً. أهلاً بعودتك!',
}


def _migrate(conn):
    """Add any missing columns to existing tables (idempotent)."""
    # users table: new permission columns
    user_cols = {r['name'] for r in conn.execute("PRAGMA table_info(users)")}
    for col in ('can_export', 'can_backup', 'can_products', 'can_sessions',
                'can_staff', 'can_whatsapp', 'can_daily_reports', 'can_monthly_reports'):
        if col not in user_cols:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} INTEGER DEFAULT 0")
    # products table: barcode_path and barcode columns
    prod_cols = [c[1] for c in conn.execute("PRAGMA table_info(products)").fetchall()]
    if 'barcode_path' not in prod_cols:
        conn.execute("ALTER TABLE products ADD COLUMN barcode_path TEXT")
    if 'barcode' not in prod_cols:
        conn.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
    conn.commit()


def init_db():
    """Create schema and seed default data."""
    ensure_dirs()
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    _migrate(conn)
    # Seed settings
    for k, v in DEFAULT_SETTINGS.items():
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()

    # Seed a default super admin if no users exist
    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()['c'] == 0:
        from werkzeug.security import generate_password_hash
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role, is_active) "
            "VALUES (?,?,?,?,?)",
            ('admin', generate_password_hash('admin123'), 'Super Admin', 'admin', 1)
        )
    conn.commit()
    conn.close()
