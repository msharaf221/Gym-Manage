from fontTools.ttLib import TTFont
import sys

font = TTFont("static/fonts/Cairo-Variable.ttf")
cmap = font.getBestCmap()
print("U+0627 (Alef) in font:", 0x0627 in cmap)
print("U+FE8D (Alef isolated) in font:", 0xFE8D in cmap)
