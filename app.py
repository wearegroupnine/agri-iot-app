#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 11:13:49 2024

@author: wangxinping
"""
import cv2
import numpy as np
from flask import Flask, render_template, send_from_directory, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import os
from flask_uploads import UploadSet, IMAGES, configure_uploads
import requests

from base64 import b64encode
import io
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadFileForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, "Only images are allowed"),
                                  FileRequired("File field should not be empty")])
    submit = SubmitField("Upload File")

@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


def format_image(img):
    file_object = io.BytesIO()
    img = Image.fromarray(img.astype('uint8'))
    img.save(file_object, 'PNG')
    base64img = "data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii')
    return base64img

def BGRtoRGB(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        print("form validate")
        filename = photos.save(form.photo.data)
        file_url = url_for("get_file", filename=filename)
        raw_img = cv2.imread(f".{file_url}")
        data = {"img":raw_img.tolist()}
        
        response = requests.post("http://localhost:6600/prediction", json=data)
        response = response.json()
        ai_img = np.array(response["ai"]).astype(np.uint8)
        disease_img = np.array(response["disease"]).astype(np.uint8)
        
        raw_base64 = format_image(BGRtoRGB(raw_img))
        ai_base64 = format_image(BGRtoRGB(ai_img))
        disease_base64 = format_image(BGRtoRGB(disease_img))
        
    else :
        file_url = None
        raw_base64 = None
        ai_base64 = None
        disease_base64 = None
    return render_template('index.html', form=form, file_url=file_url, \
                                             ai=ai_base64, \
                                             disease=disease_base64,)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port="5121")
