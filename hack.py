import pdf2image as p2i
import numpy as np
from PIL import Image
import math

x = input("Enter Url of the pdf")
pic = p2i.convert_from_path(r"".join(x))
np_im = np.array(pic[0])
np_im.shape


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


gray = rgb2gray(np_im)
gray.shape
i = 1
while i < gray.shape[1]:
    if gray[:, i].min() < 90:
        gray = gray[:, i - 10:]
        break
    i += 1
i = 1
while i < gray.shape[0]:
    if gray[i, :].min() < 90:
        gray = gray[i - 10:, :]
        break
    i += 1
i = gray.shape[1] - 1
while i > 1:
    if gray[:, i].min() < 90:
        gray = gray[:, :i + 10]
        break
    i -= 1
i = gray.shape[0] - 1
while i > 1:
    if gray[i, :].min() < 90:
        gray = gray[:i + 10, :]
        break
    i -= 1


def cleanwhitespaces(gray):
    i = 1
    while i < gray.shape[1]:
        if gray[:, i].min() < 90:
            gray = gray[:, i - 1:]
            break
        i += 1
    i = gray.shape[1] - 1
    while i > 1:
        if gray[:, i].min() < 90:
            gray = gray[:, :i + 3]
            break
        i -= 1
    return gray


def api_call(im):
    url = 'https://api.mathpix.com/v3/latex'
    headers = {'content-type': 'application/json', 'app_key': 'hophacks2019',
               'app_id': 'hophacks'}
    buffered = BytesIO()
    im.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    payload = {'src': "data:image/jpeg;base64," + img_str.decode('utf-8'),
               "ocr": ["math", "text"],
               "skip_recrop": True,
               "formats": [
                   "text",
                   "latex_simplified",
                   "latex_styled",
                   "mathml",
                   "asciimath",
                   "latex_list"
               ]
               }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    return r

print('calling api...')
import requests
import json
import base64
from io import BytesIO

linecount = 0
i = 1
start = 0
end = 0
latexjson = []
while i < gray.shape[0] - 1:
    if gray[i, :].min() < 90:
        start = i
        while gray[i, :].min() < 90:
            i += 1
        end = i
        breakpoint = int(math.floor((gray.shape[1]) / 2) - math.floor(0.2 * (gray.shape[1]) / 2))
        count = 0

        for x in range(int(breakpoint - 0.2 * breakpoint), int(breakpoint + 0.2 * breakpoint)):
            while gray[start - 2:end + 2, x].min() > 90:
                count += 1
                x += 1
                if count > 5: break
            if count > 5:
                breakpoint = x - 2
                line = gray[start - 2:end + 2, :breakpoint]
                line = cleanwhitespaces(line)
                im = Image.fromarray(line)
                im = im.convert("L")
                filename = 'C:\\Users\\Nikesh\\Desktop\\Split\\line' + str(linecount) + '.jpeg'
                im.save(filename)
                linecount += 1
                r = api_call(im)
                json_data = json.loads(r.text)
                latexjson.append(r.json())
                break
            else:
                count = 0
        line = gray[start - 2:end + 2, breakpoint:]
        line = cleanwhitespaces(line)
        im = Image.fromarray(line)
        im = im.convert("L")
        filename = 'C:\\Users\\Nikesh\\Desktop\\Split\\line' + str(linecount) + '.jpeg'
        im.save(filename)
        linecount += 1
        r = api_call(im)
        json_data = json.loads(r.text)
        latexjson.append(r.json())
    i += 1
totallatex = ''
y = 1
key = "latex_styled"
for dic in latexjson:
    y += 1
    if key in dic:
        totallatex += dic[key]
        if y % 2 == 1:
            totallatex += " \\\ "
        else:
            totallatex += ' '
totallatex = '$' + totallatex + '$'
braillelatex = totallatex
braillelatex = braillelatex.replace('\\text', '\\textbraille')
braillefile = '\\documentclass{article} \\usepackage{fontspec} \\usepackage{amsfonts} \\newfontfamily\\braillefont{ghUBraille} \\DeclareTextFontCommand{\\textbraille}{\\braillefont} \\begin{document} ' + braillelatex + ' \\end{document}'
latexfile = '\\documentclass{article} \\usepackage{amsmath} \\usepackage{amsfonts} \\usepackage[a4paper, total={8in, 11in}]{geometry} \\begin{document} ' + totallatex + ' \\end{document}'
import os, glob, subprocess

with open('normal.tex', 'w') as f:
    f.write(latexfile)
commandLine = subprocess.Popen(['pdflatex', 'normal.tex'])
commandLine.communicate()

os.unlink('normal.aux')
os.unlink('normal.log')
os.unlink('normal.tex')
with open('normal.tex', 'w') as f:
    f.write(latexfile)
import os, glob, subprocess

with open('braille.tex', 'w') as f:
    f.write(braillefile)
commandLine = subprocess.Popen(['xelatex', 'braille.tex'])
commandLine.communicate()

os.unlink('braille.aux')
os.unlink('braille.log')
os.unlink('braille.tex')
with open('braille.tex', 'w') as f:
    f.write(braillefile)