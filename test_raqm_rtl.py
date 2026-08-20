from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("static/fonts/Cairo-Variable.ttf", 30)
img = Image.new('RGB', (400, 100), 'white')
d = ImageDraw.Draw(img)
d.text((10, 10), "محمد حسين", font=font, fill='black', direction='rtl', language='ar')
img.save('test_raqm_rtl.png')
