import sys
from PIL import Image, ImageFont, ImageDraw
from bidi.algorithm import get_display
import arabic_reshaper

font_path = "static/fonts/Cairo-Variable.ttf"
try:
    font = ImageFont.truetype(font_path, 30)
except:
    font = ImageFont.load_default()

text = "عمر احمد السيد"

img = Image.new('RGB', (400, 200), 'white')
d = ImageDraw.Draw(img)

# 1. Raw text (Raqm handles it)
d.text((10, 10), text, font=font, fill='black')

# 2. Reshaped text (What the app currently does)
reshaped = get_display(arabic_reshaper.reshape(text))
d.text((10, 50), reshaped, font=font, fill='red')

img.save('test_raqm.png')
print("Saved test_raqm.png")
