from fastapi import FastAPI, UploadFile,File
import uvicorn

import shutil
import os

import os
import numpy as np
from PIL import Image
import keras
from keras.models import load_model

import json


app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/bad/")
async def root():
    return {"message":"bad"}

@app.post("/files/")
async def file(file: bytes = File(...)):
    content = file.decode('utf-8')
    formatfile = content.split('\n')
    return {'filedetail': formatfile}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if file:
        filename = file.filename
        fileobj = file.file
        upload_dir = open(os.path.join("../uploads/", filename),'wb+')
        shutil.copyfileobj(fileobj, upload_dir)
        upload_dir.close()
        return {"アップロードファイル名": filename}
    return {"Error": "アップロードファイルが見つかりません。"}

@app.post("/cat_or_dog/")
async def upload_file(file: UploadFile = File(...)):
    if file:
        filename = file.filename
        fileobj = file.file
        
        result = catORdog(fileobj)
        
        if result[0] == 0:
            result[0] = "dog"
        else:
            result[0] = "cat"

        return {"filename": filename, "result": result[0], "prd":result[1]}
    return {"Error": "アップロードファイルが見つかりません。"}

@app.get("/product/all")
async def get_all():
    json_open = open('../src/product.json', 'r')
    json_load = json.load(json_open)
    return json_load

@app.get("/product/")
async def get(id: int=0):
    json_open = open('../src/product.json', 'r')
    json_load = json.load(json_open)
    for i in json_load["contents"]:
        if i["id"] == id:
            return i
    return {"Error": "コンテンツが見つかりません。"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
    
def catORdog(fileobj):
        imsize = (64, 64)

        def load_image(path):
            img = Image.open(path)
            img = img.convert('RGB')
            # 学習時に、(64, 64, 3)で学習したので、画像の縦・横は今回 変数imsizeの(64, 64)にリサイズします。
            img = img.resize(imsize)
            # 画像データをnumpy配列の形式に変更
            img = np.asarray(img)
            img = img / 255.0
            return img

        model = load_model("../src/cnn.h5")
        img = load_image(fileobj)
        prd = model.predict(np.array([img]))
        prelabel = np.argmax(prd, axis=1)
        result = []
        result.append(prelabel)
        result.append(str(prd[0]))
        return result