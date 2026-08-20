import sys
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    text = "عمر احمد السيد"
    reshaped = arabic_reshaper.reshape(text)
    display = get_display(reshaped)
    print("SUCCESS")
    print(display)
except Exception as e:
    print("ERROR")
    print(e)
