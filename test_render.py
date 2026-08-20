import sys
from PIL import Image, ImageFont, ImageDraw
import arabic_reshaper
from bidi.algorithm import get_display

text = "عمر احمد السيد"
reshaped = arabic_reshaper.reshape(text)
display = get_display(reshaped)
print("Display string repr:", repr(display))

font_path = "static/fonts/Cairo-Variable.ttf"
try:
    font = ImageFont.truetype(font_path, 30)
except:
    font = ImageFont.load_default()

img = Image.new('RGB', (400, 100), 'white')
d = ImageDraw.Draw(img)
d.text((10, 10), display, font=font, fill='black')
img.save('test_render.png')
