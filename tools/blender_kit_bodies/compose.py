"""Assemble les planches contact à partir des tuiles rendues (jobs_*.json). Python du venv (Pillow)."""
import json, sys, os, glob
from PIL import Image, ImageDraw, ImageFont


def font(sz):
    for p in ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/SFNS.ttf', '/Library/Fonts/Arial.ttf'):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def sheet(job, bg=(70, 73, 80)):
    tw, th = job['tile']
    cols = job['cols']
    n = len(job['images'])
    rows = (n + cols - 1) // cols
    top = 34 if job.get('title') else 0
    im = Image.new('RGB', (cols * tw, rows * th + top), bg)
    d = ImageDraw.Draw(im)
    if job.get('title'):
        d.text((10, 8), job['title'], fill=(240, 240, 240), font=font(18))
    for i, (img, lab) in enumerate(zip(job['images'], job['labels'])):
        x, y = (i % cols) * tw, (i // cols) * th + top
        if isinstance(img, list):
            w1 = tw // len(img)
            for j, one in enumerate(img):
                t = Image.open(one).convert('RGB')
                # recadrage centré au format de la demi-tuile
                r = w1 / th
                W, H = t.size
                cw = int(H * r)
                x0 = (W - cw) // 2
                t = t.crop((x0, 0, x0 + cw, H)).resize((w1, th), Image.LANCZOS)
                im.paste(t, (x + j * w1, y))
        else:
            t = Image.open(img).convert('RGB').resize((tw, th), Image.LANCZOS)
            im.paste(t, (x, y))
        d.text((x + 8, y + 6), lab, fill=(255, 255, 255), font=font(14))
    im.save(job['path'])


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    tmp = os.path.join(here, '..', '..', 'assets', 'models', 'kit', 'preview', '_tmp')
    pats = sys.argv[1:] or ['*']
    for pat in pats:
        for jf in glob.glob(os.path.join(tmp, f'jobs_{pat}.json')):
            for job in json.load(open(jf)):
                sheet(job)
                print('sheet', job['path'])
