from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import io
import cv2
import pytesseract
import numpy as np
import requests
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="ocrpytesseract/static"), name="static")

templates = Jinja2Templates(directory="ocrpytesseract/templates")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

class ImageType(BaseModel):
    url: str


def getLang(x, lang):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    #pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    if (lang == 'eng'):
        x = pytesseract.image_to_string(x, lang='tha')
    elif (lang == 'tha'):
        x = pytesseract.image_to_string(x, lang='eng')
    else:
        x = pytesseract.image_to_string(x)
    return x

def getLangNoLang(x):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    #pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    x = pytesseract.image_to_string(x)
    return x

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

@app.post("/")
async def readFile(request: Request, image_upload: UploadFile = File(...)):
    # file upload
    data = await image_upload.read()
    filename = image_upload.filename

    with open(filename, 'wb') as f:
        f.write(data)

    # template
    FILE_PATH = 'https://i.ibb.co/rG4Hty9/template.jpg'
    response = requests.get(FILE_PATH)
    template_filename = 'ocrpytesseract/static/template.jpg'

    with open(template_filename, 'wb') as f:
        f.write(response.content)

    ###
    per = 25
    pixelThreshold = 500

    roi = [
           [(752, 108), (1410, 212), 'text', 'id'],
           [(486, 206), (1460, 332), 'th', 'name'],
           [(658, 332), (1236, 400), 'en', 'firstname'],
           [(758, 410), (1432, 480), 'en', 'lastname'],
           [(748, 482), (1164, 576), 'th', 'hbd'],
           [(864, 572), (1260, 640), 'en', 'hbd-en'],
           [(720, 652), (994, 714), 'th', 'region'],
           [(148, 708), (1264, 870), 'th', 'address']
          ]

    orb = cv2.ORB_create(10000)

    #template
    imgQ = cv2.imread(template_filename)
    h, w, c = imgQ.shape
    orb = cv2.ORB_create(1000)
    kp1, des1 = orb.detectAndCompute(imgQ, None)

    #file upload
    img = cv2.imread(filename)
    kp2, des2 = orb.detectAndCompute(img, None)

    #compare
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.match(des2, des1)
    matches.sort(key=lambda x: x.distance)
    good = matches[:int(len(matches) * (per / 100))]

    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, _ = cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)
    imgScan = cv2.warpPerspective(img, M, (w, h))

    myData = dict()

    for x, r in enumerate(roi):
        imgCrop = imgScan[r[0][1]:r[1][1], r[0][0]:r[1][0]]

        if r[2] == 'text':
            x = getLangNoLang(imgCrop)
            myData[r[3]] = x.replace('\f','').replace('\n','')

        if r[2] == 'th':
            x = getLang(imgCrop, 'eng')
            myData[r[3]] = x.replace('\f','').replace('\n','')

        if r[2] == 'en':
            x = getLang(imgCrop, 'tha')
            myData[r[3]] = x.replace('\f','').replace('\n','')
    return myData

if __name__ == '__main__':
    uvicorn.run(app, debug=True)
