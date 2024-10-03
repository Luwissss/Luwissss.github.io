import pytesseract
from PIL import Image
from flask import Flask, request, render_template, redirect, url_for, session, Response, flash, jsonify
import re
import io 
import requests
import base64
import sqlite3
import csv

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/')
def home():
    return render_template("ar2.html")



if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(ssl_context='adhoc')
