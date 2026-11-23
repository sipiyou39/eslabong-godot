import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
PV = ASSETS + '/ui/preview'
def folder_sheet(folder, out, cols, cell, names=None, scale=None):
    files = sorted(glob.glob(f'{folder}/*.png')) if names is None else [f'{folder}/{n}.png' for n in names]
    ims = [Image.open(f).convert('RGBA') for f in files]
    if scale:
        ims = [i.resize((int(i.width * scale), int(i.height * scale)), Image.LANCZOS) for i in ims]
    contact(ims, cols, cell, out, bg=(44, 48, 62), pad=4)
if __name__ == '__main__':
    k = sys.argv[1]
    if k == 'ui':
        folder_sheet(ASSETS + '/ui/icons', PV + '/ui_icons.png', 13, 80, scale=1.6)
    if k == 'status':
        folder_sheet(ASSETS + '/icons/status', PV + '/status_icons.png', 11, 84, scale=2.4)
