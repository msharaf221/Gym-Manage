import app
app.init_db()

with app.app.test_request_context():
    print("Testing...")
    try:
        app.regen_barcode(8350)
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()
