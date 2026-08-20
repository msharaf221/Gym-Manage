"""
Power Home Gym Management System - Utilities
Business-day/month logic, barcode/QR generation, WhatsApp, audit, notifications.
"""
import os
import json
import requests
from datetime import datetime, timedelta, date

from db import get_connection, BARCODE_DIR, UPLOAD_DIR
import arabic_reshaper
from bidi.algorithm import get_display

arabic_config = {
    'use_unshaped_instead_of_isolated': True,
    'support_ligatures': False
}
reshaper = arabic_reshaper.ArabicReshaper(configuration=arabic_config)

# ---------------------------------------------------------------------------
# Plan types and durations
# ---------------------------------------------------------------------------
PLANS = {
    'month': {'days': 30, 'label': 'شهري'},
    'month_cardio': {'days': 30, 'label': 'شهري (كارديو)'},
    '15days': {'days': 15, 'label': '15 يوم'},
    'half_cardio': {'days': 15, 'label': '15 يوم (كارديو)'},
    'quarter': {'days': 90, 'label': 'ربع سنوي'},
    'half_year': {'days': 180, 'label': 'نصف سنوي'},
    'year': {'days': 365, 'label': 'سنوي'},
}

PERMISSIONS = [
    ('can_add_members', 'إضافة أعضاء'),
    ('can_view_members', 'عرض الأعضاء'),
    ('can_edit_members', 'تعديل الأعضاء'),
    ('can_delete_members', 'حذف الأعضاء'),
    ('can_checkin', 'تسجيل الحضور'),
    ('can_sales', 'المبيعات'),
    ('can_delete_sales', 'حذف المبيعات'),
    ('can_products', 'إدارة المنتجات'),
    ('can_sessions', 'الحصص اليومية'),
    ('can_delete_sessions', 'حذف الحصص'),
    ('can_view_finance', 'عرض المالية'),
    ('can_withdrawals', 'المصروفات'),
    ('can_delete_withdrawals', 'حذف المصروفات'),
    ('can_staff', 'الموظفون والرواتب'),
    ('can_daily_reports', 'التقارير اليومية'),
    ('can_monthly_reports', 'التقارير المالية/الشهرية'),
    ('can_export', 'التصدير (Excel)'),
    ('can_backup', 'النسخ الاحتياطي والاستعادة'),
    ('can_whatsapp', 'رسائل واتساب'),
    ('can_manage_users', 'إدارة المستخدمين'),
    ('can_settings', 'الإعدادات'),
    ('can_audit', 'سجل العمليات'),
]

# All permission column names (for seeding admins / migrations)
ALL_PERMISSION_COLS = [key for key, _ in PERMISSIONS]


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row is None:
        return default
    return row['value']


def get_all_settings():
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, str(value)))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Business day / month logic
# ---------------------------------------------------------------------------
def business_date(now=None):
    """Business day: day rolls over at day_start_hour (default 4 AM)."""
    now = now or datetime.now()
    day_start = int(get_setting('day_start_hour', '4') or 4)
    d = now.date()
    if now.hour < day_start:
        d = d - timedelta(days=1)
    return d


def business_month(bd=None):
    """Business month: starts at month_start_day (default 25th)."""
    bd = bd or business_date()
    month_start = int(get_setting('month_start_day', '25') or 25)
    if bd.day >= month_start:
        return bd.strftime('%Y-%m')
    first = bd.replace(day=1)
    prev = first - timedelta(days=1)
    return prev.strftime('%Y-%m')


def business_month_bounds(year_month):
    """Return (start_date, end_date) for a business month label."""
    y, m = map(int, year_month.split('-'))
    month_start = int(get_setting('month_start_day', '25') or 25)
    start = date(y, m, month_start)
    if m == 12:
        end = date(y + 1, 1, month_start) - timedelta(days=1)
    else:
        end = date(y, m + 1, month_start) - timedelta(days=1)
    return start, end


# ---------------------------------------------------------------------------
# Barcode / QR generation (Code128 with Arabic name support)
# ---------------------------------------------------------------------------
FONT_DIR = os.path.join(os.path.dirname(BARCODE_DIR), 'fonts')

_font_cache = {}


def _ar(text):
    """Reshape + apply bidi so Arabic renders correctly (visual order) in PIL.

    If PIL has Raqm support, it handles Arabic natively, so we return the text as-is.
    Otherwise, we use arabic_reshaper and bidi.
    """
    if not text:
        return ''
    
    from PIL import features
    if features.check('raqm'):
        return str(text)

    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        
        # أضف هذه الإعدادات لمنع حذف الحروف (مثل الألف والراء)
        arabic_config = {
            'use_unshaped_instead_of_isolated': True,
            'support_ligatures': False
        }
        reshaper = arabic_reshaper.ArabicReshaper(configuration=arabic_config)
        return get_display(reshaper.reshape(str(text)))
        
    except Exception:
        return str(text)[::-1]
def _ar_value(ar_label, value):
    """Arabic label + an LTR value (date/number) - keeps the value intact."""
    return _ar(f'{ar_label} \u202a{value}\u202ac')

def _font(size, weight=400):
    """Load Cairo (variable) with a given weight; fallback to any Arabic TTF."""
    from PIL import ImageFont
    key = (size, weight)
    if key in _font_cache:
        return _font_cache[key]
    candidates = ['Cairo-Variable.ttf', 'Amiri-Regular.ttf', 'NotoNaskhArabic.ttf']
    for name in candidates:
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size)
                if 'Cairo' in name or 'Naskh' in name:
                    try:
                        f.set_variation_by_axes([weight])
                    except Exception:
                        pass
                _font_cache[key] = f
                return f
            except Exception:
                continue
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


# Physical label size: 60mm x 20mm @ 300 DPI
LABEL_DPI = 300
LABEL_W = 449   # 38 mm @ 300 DPI
LABEL_H = 295   # 25 mm @ 300 DPI

def _render_code128(value, target_width=None, module_height=14.0):
    """Return a PIL Image of a Code128 barcode (no human-readable text)."""
    import barcode
    from barcode.writer import ImageWriter
    code = barcode.get('code128', str(value), writer=ImageWriter())
    # Increase module_width to make it wider by default
    opts = {'write_text': False, 'module_height': module_height,
            'module_width': 0.55, 'quiet_zone': 2.0, 'dpi': LABEL_DPI}
    img = code.render(writer_options=opts)
    
    if target_width:
        from PIL import Image
        if img.width > target_width:
            ratio = target_width / img.width
            new_h = int(img.height * ratio)
            img = img.resize((target_width, new_h), Image.LANCZOS)
        elif img.width < target_width:
            # Scale up (stretch width only)
            img = img.resize((target_width, img.height), Image.NEAREST)
    return img


def _fit_font(d, text, size, weight, max_width, min_size=14):
    """Shrink font until the text fits within max_width."""
    s = size
    while s > min_size:
        f = _font(s, weight)
        if d.textlength(text, font=f) <= max_width:
            return f, s
        s -= 2
    return _font(min_size, weight), min_size


def _wrap_text(d, text, font, max_width):
    """Wrap text (by spaces) into lines that fit max_width."""
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if not cur:
            cur = w
        elif d.textlength(t, font=font) <= max_width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_wrapped(d, text, size, weight, max_width, max_lines=2, min_size=12):
    """Shrink font until text wraps within max_lines lines."""
    s = size
    while s > min_size:
        f = _font(s, weight)
        lines = _wrap_text(d, text, f, max_width)
        if len(lines) <= max_lines:
            return f, lines, s
        s -= 2
    f = _font(min_size, weight)
    lines = _wrap_text(d, text, f, max_width)
    return f, lines[:max_lines], min_size


def _draw_center(d, text, font, y, width, fill=(0, 0, 0), x0=0):
    tw = d.textlength(text, font=font)
    x = x0 + (width - tw) / 2
    d.text((x, y), text, font=font, fill=fill)


def _draw_lines_center(d, lines, font, x0, x1, y, line_h, fill=(0, 0, 0)):
    """Draw wrapped lines centered horizontally between x0..x1, starting at y."""
    width = x1 - x0
    for i, ln in enumerate(lines):
        _draw_center(d, ln, font, y + i * line_h, width, fill=fill, x0=x0)
    return y + len(lines) * line_h


def generate_member_ticket(member_id, name, plan_label='', end_date='', phone='', gym_name=None):
    """
    Generate a printable membership label sized 38mm x 25mm @ 300 DPI (449x295 px).
    Vertical stacked layout.
    """
    from PIL import Image, ImageDraw

    gym_name = gym_name or get_setting('gym_name', 'Power Home')
    W, H = LABEL_W, LABEL_H
    PRIMARY = (37, 99, 235)
    DARK = (17, 24, 39)

    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    # Gym name (Top)
    # gym_txt = _ar(gym_name)
    # f_gym, _ = _fit_font(d, gym_txt, 26, 800, W - 20, 14)
    # _draw_center(d, gym_txt, f_gym, 12, W, fill=PRIMARY, x0=0)

    # Member Name
    name_txt = _ar(name)
    f_name, lines, _ = _fit_wrapped(d, name_txt, 22, 700, W - 20, max_lines=2, min_size=10)
    y_after_name = _draw_lines_center(d, lines, f_name, 0, W, 15, 36, fill=DARK)

    # Barcode
    BAR_MAX_W = W - 10
    bar_img = _render_code128(member_id, target_width=BAR_MAX_W, module_height=10.0)
    
    space_left = H - y_after_name
    by = y_after_name + (space_left - bar_img.height - 35) // 2
    if by < y_after_name + 5: by = y_after_name + 5
    
    bx = (W - bar_img.width) // 2
    img.paste(bar_img, (bx, by))

    # Member ID
    f_id = _font(32, 800)
    _draw_center(d, str(member_id), f_id, by + bar_img.height + 5, W, fill=DARK, x0=0)
    
    path = os.path.join(BARCODE_DIR, f'member_{member_id}.png')
    img.save(path, dpi=(LABEL_DPI, LABEL_DPI))
    return f'/static/barcodes/member_{member_id}.png'


def generate_product_barcode(product_id, product_name, price=None, barcode_val=None):
    """Generate a printable product label sized 38mm x 25mm @ 300 DPI (449x295 px)."""
    from PIL import Image, ImageDraw
    import os

    if barcode_val is None:
        barcode_val = product_id

    W, H = LABEL_W, LABEL_H
    DARK = (17, 24, 39)
    GREEN = (22, 163, 74)

    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    # Product name (Top)
    name_txt = _ar(product_name)
    f_name, lines, _ = _fit_wrapped(d, name_txt, 28, 700, W - 20, max_lines=2, min_size=16)
    y_after_name = _draw_lines_center(d, lines, f_name, 0, W, 10, 32, fill=DARK)

    # Price
    if price is not None:
        f_price = _font(28, 700)
        _draw_center(d, _ar_value('', f'{price} {get_setting("currency", "EGP")}'),
                     f_price, y_after_name + 5, W, fill=GREEN, x0=0)
        y_after_name += 35

    # Barcode
    BAR_MAX_W = W - 30
    bar_img = _render_code128(barcode_val, target_width=BAR_MAX_W, module_height=16.0)
    
    space_left = H - y_after_name
    by = y_after_name + (space_left - bar_img.height - 30) // 2
    if by < y_after_name + 5: by = y_after_name + 5
    
    bx = (W - bar_img.width) // 2
    img.paste(bar_img, (bx, by))

    # Product ID / Barcode Val
    f_id = _font(26, 800)
    _draw_center(d, str(barcode_val), f_id, by + bar_img.height + 5, W, fill=DARK, x0=0)

    path = os.path.join(BARCODE_DIR, f'product_{product_id}.png')
    img.save(path, dpi=(LABEL_DPI, LABEL_DPI))
    return f'/static/barcodes/product_{product_id}.png'


def generate_barcode(member_id, text):
    """Backward-compatible wrapper: generate a membership ticket."""
    return generate_member_ticket(member_id, text)


def generate_qr(member_id):
    """Generate a QR code encoding the member ID."""
    import qrcode
    img = qrcode.make(f'POWERHOME:{member_id}')
    path = os.path.join(BARCODE_DIR, f'qr_{member_id}.png')
    img.save(path)
    return f'/static/barcodes/qr_{member_id}.png'


def regenerate_all_tickets():
    """Regenerate every member ticket and product label.

    Called on app startup so labels are always correct even if they were
    generated earlier while Arabic-shaping libraries were unavailable.
    """
    gym_name = get_setting('gym_name', 'Power Home')
    conn = get_connection()
    try:
        members = conn.execute("SELECT * FROM members").fetchall()
        for m in members:
            sub = conn.execute(
                "SELECT * FROM subscriptions WHERE member_id = ? ORDER BY sub_id DESC LIMIT 1",
                (m['id'],)).fetchone()
            plan = sub['plan_type'] if sub else ''
            plan_label = PLANS.get(plan, {}).get('label', plan) if plan else ''
            end = sub['end_date'] if sub else ''
            p = generate_member_ticket(m['id'], m['full_name'], plan_label, end,
                                       m['phone'], gym_name)
            conn.execute("UPDATE members SET barcode_path = ? WHERE id = ?", (p, m['id']))
        products = conn.execute("SELECT * FROM products").fetchall()
        for pr in products:
            p = generate_product_barcode(pr['product_id'], pr['product_name'], pr['price'])
            conn.execute("UPDATE products SET barcode_path = ? WHERE product_id = ?",
                         (p, pr['product_id']))
        conn.commit()
    finally:
        conn.close()


def normalize_phone(phone):
    """Normalize a phone number to Egyptian international format (+20...)."""
    if not phone:
        return phone
    phone = ''.join(ch for ch in str(phone) if ch.isdigit() or ch == '+')
    if phone.startswith('00'):
        phone = '+' + phone[2:]
    if phone.startswith('0'):
        phone = '+2' + phone
    elif phone.startswith('20') and not phone.startswith('+'):
        phone = '+' + phone
    return phone


# ---------------------------------------------------------------------------
# WhatsApp (Cloud API primary, pywhatkit fallback)
# ---------------------------------------------------------------------------
def send_whatsapp(phone, message):
    """Send a WhatsApp message. Returns (ok: bool, error: str)."""
    if str(get_setting('whatsapp_enabled', '1')) != '1':
        return False, 'WhatsApp disabled in settings'
    phone = normalize_phone(phone)
    if not phone:
        return False, 'No phone number'

    # Primary: WhatsApp Cloud API
    token = get_setting('whatsapp_token', '')
    phone_id = get_setting('whatsapp_phone_id', '')
    if token and phone_id:
        try:
            url = f'https://graph.facebook.com/v18.0/{phone_id}/messages'
            headers = {'Authorization': f'Bearer {token}',
                       'Content-Type': 'application/json'}
            payload = {
                'messaging_product': 'whatsapp',
                'to': phone,
                'type': 'text',
                'text': {'body': message},
            }
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            if r.status_code == 200:
                return True, ''
            return False, f'Cloud API error {r.status_code}: {r.text[:200]}'
        except Exception as e:
            return False, f'Cloud API exception: {e}'

    # Fallback: pywhatkit (desktop automation) - optional
    try:
        import pywhatkit
        pywhatkit.sendwhatmsg_instantly(phone, message, 10, True, 3)
        return True, ''
    except Exception as e:
        return False, f'pywhatkit unavailable: {e}'


def enqueue_whatsapp(member_id, phone, message, msg_type):
    conn = get_connection()
    conn.execute(
        "INSERT INTO whatsapp_queue (member_id, phone, message, msg_type) "
        "VALUES (?,?,?,?)", (member_id, phone, message, msg_type))
    conn.commit()
    conn.close()


def render_template_text(template, member, subscription=None):
    """Fill a message template with dynamic variables."""
    t = template or ''
    bd = business_date()
    remaining = 0
    days_left = 0
    expiry = ''
    if subscription:
        remaining = max(0, (subscription['price'] or 0) - (subscription['amount_paid'] or 0))
        if subscription['end_date']:
            expiry = subscription['end_date']
            try:
                end = datetime.strptime(expiry, '%Y-%m-%d').date()
                days_left = (end - bd).days
            except Exception:
                days_left = 0
    repl = {
        '{gym_name}': get_setting('gym_name', 'Power Home'),
        '{member_name}': member['full_name'] or '',
        '{member_id}': str(member['id']),
        '{phone}': member['phone'] or '',
        '{expiry_date}': expiry,
        '{start_date}': subscription['start_date'] if subscription else '',
        '{remaining_amount}': str(remaining),
        '{days_left}': str(days_left),
        '{freeze_date}': member['freeze_start'] or '',
    }
    for k, v in repl.items():
        t = t.replace(k, str(v))
    return t


# ---------------------------------------------------------------------------
# Audit + notifications
# ---------------------------------------------------------------------------
def log_audit(user_id, action, entity_type=None, entity_id=None,
              old_values=None, new_values=None, request=None):
    ip = ua = None
    if request:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        ua = (request.headers.get('User-Agent', '') or '')[:300]
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_values, "
        "new_values, ip_address, user_agent) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, action, entity_type, entity_id,
         json.dumps(old_values, ensure_ascii=False) if old_values else None,
         json.dumps(new_values, ensure_ascii=False) if new_values else None,
         ip, ua))
    conn.commit()
    conn.close()


def add_notification(user_id, title, message, notif_type='info'):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notifications (user_id, title, message, notif_type) VALUES (?,?,?,?)",
        (user_id, title, message, notif_type))
    conn.commit()
    conn.close()


def notify_admins(title, message, notif_type='info'):
    conn = get_connection()
    admins = conn.execute("SELECT id FROM users WHERE role = 'admin'").fetchall()
    for a in admins:
        conn.execute(
            "INSERT INTO notifications (user_id, title, message, notif_type) VALUES (?,?,?,?)",
            (a['id'], title, message, notif_type))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Cash flow ledger
# ---------------------------------------------------------------------------
def record_cash_flow(flow_type, source_table, source_id, direction, amount,
                     reason, payment_method='cash', created_by=None, meta=None):
    bd = business_date()
    bm = business_month(bd)
    conn = get_connection()
    conn.execute(
        "INSERT INTO cash_flow (flow_type, source_table, source_id, direction, amount, "
        "reason, business_date, business_month, payment_method, created_by, meta_json) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (flow_type, source_table, source_id, direction, amount, reason,
         bd.isoformat(), bm, payment_method, created_by,
         json.dumps(meta, ensure_ascii=False) if meta else None))
    conn.commit()
    conn.close()


def member_subscription(member_id):
    """Return the member's latest/active subscription row."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM subscriptions WHERE member_id = ? ORDER BY sub_id DESC LIMIT 1",
        (member_id,)).fetchone()
    conn.close()
    return row


def member_status(member):
    """Compute active/expired/frozen status for a member row (Row or dict)."""
    if isinstance(member, dict):
        m = member
    else:
        m = dict(member)
    if m.get('is_frozen'):
        return 'frozen'
    sub = member_subscription(m['id'])
    if not sub:
        return 'expired'
    bd = business_date()
    try:
        end = datetime.strptime(sub['end_date'], '%Y-%m-%d').date()
        if end >= bd:
            return 'active'
    except Exception:
        pass
    return 'expired'
