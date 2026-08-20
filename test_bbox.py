from PIL import Image, ImageDraw, ImageFont

font_path = "static/fonts/Cairo-Variable.ttf"
font = ImageFont.truetype(font_path, 30)

img = Image.new('RGB', (400, 100), 'white')
d = ImageDraw.Draw(img)

bb1 = d.textbbox((0, 0), "محمد حسين", font=font)
try:
    bb2 = d.textbbox((0, 0), "محمد حسين", font=font, direction='rtl', language='ar')
except Exception as e:
    bb2 = str(e)

print("Default bbox:", bb1)
print("RTL bbox:", bb2)
