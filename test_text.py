import arabic_reshaper
from bidi.algorithm import get_display

text = "عمر احمد السيد"
print("Original:", text)
reshaped = arabic_reshaper.reshape(text)
print("Reshaped:", reshaped)
display = get_display(reshaped)
print("Display:", display)
