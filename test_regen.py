import app
app.init_db()
from utils import generate_member_ticket, generate_product_barcode
print(generate_member_ticket(12, "خالد صبحي زريبه", "شهر", "2018-08-01"))
print(generate_product_barcode(1, "عصير تفاح", 15.0, "123456789"))
