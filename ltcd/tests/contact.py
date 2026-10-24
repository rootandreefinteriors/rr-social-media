"""contact sheet: python contact.py out.png still_*.png  (labels each with its time)"""
import sys, glob
from PIL import Image, ImageDraw
out, files = sys.argv[1], sorted(sum([glob.glob(a) for a in sys.argv[2:]], []))
tw, th, cols = 270, 480, 6
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 24)), "white")
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th))
    x, y = (i % cols) * tw, (i // cols) * (th + 24)
    sheet.paste(im, (x, y + 24)); d.text((x + 6, y + 4), f.split("still_")[-1].replace(".png", "s"), fill="black")
    d.rectangle([x, y + 24, x + tw - 1, y + 24 + th - 1], outline="#999")
sheet.save(out); print(out, len(files))
