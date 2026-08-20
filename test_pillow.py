from PIL import Image, ImageDraw, ImageFont

font_path = "static/fonts/Cairo-Variable.ttf"
font = ImageFont.truetype(font_path, 30)

img = Image.new('RGB', (400, 100), 'white')
d = ImageDraw.Draw(img)

# 1. Without direction or language
d.text((10, 10), "محمد حسين", font=font, fill='black')

# 2. With direction
try:
    d.text((10, 50), "محمد حسين", font=font, fill='red', direction='rtl', language='ar')
except Exception as e:
    d.text((10, 50), str(e), fill='red')

img.save('test_pillow.png')
print("Done")
