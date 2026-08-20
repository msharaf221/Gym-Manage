from PIL import Image, ImageDraw
import utils
from utils import _render_code128, _ar, _fit_font, _draw_center, _font, _fit_wrapped, _draw_lines_center
import os

LABEL_W = 449
LABEL_H = 295

def generate_test_member():
    W, H = LABEL_W, LABEL_H
    PRIMARY = (37, 99, 235)
    DARK = (17, 24, 39)
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    
    # Gym name (Top)
    gym_name = "Power Home"
    gym_txt = _ar(gym_name)
    f_gym, _ = _fit_font(d, gym_txt, 30, 800, W - 20, 16)
    _draw_center(d, gym_txt, f_gym, 10, W, fill=PRIMARY, x0=0)
    
    # Member Name (Below Gym Name)
    name_txt = _ar("محمد اشرف محمد عوض")
    f_name, lines, _ = _fit_wrapped(d, name_txt, 34, 700, W - 20, max_lines=2, min_size=20)
    y_after_name = _draw_lines_center(d, lines, f_name, 0, W, 50, 40, fill=DARK)
    
    # Barcode
    BAR_MAX_W = W - 40
    # Make barcode taller since we have height
    bar_img = _render_code128("123456", target_width=BAR_MAX_W, module_height=22.0)
    
    # Paste barcode
    # Calculate space left
    space_left = H - y_after_name
    by = y_after_name + (space_left - bar_img.height - 40) // 2
    if by < y_after_name + 5: by = y_after_name + 5
    
    bx = (W - bar_img.height) // 2 # WRONG, should be width
    bx = (W - bar_img.width) // 2
    img.paste(bar_img, (bx, by))
    
    # Member ID
    f_id = _font(36, 800)
    _draw_center(d, "123456", f_id, by + bar_img.height + 5, W, fill=DARK, x0=0)
    
    img.save("test_member.png")

generate_test_member()
