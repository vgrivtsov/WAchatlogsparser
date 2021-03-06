#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import timeit
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from wa_main import main as file_parsing

app = Flask(__name__)    
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt'])  

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
           
@app.route("/")
def index_template():
    return render_template('layout.html')     

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
        data_dict = file_parsing(filename)        

        return render_template('stats.html', data_dict=data_dict[0],\
               file_status="File %s processed success" % filename,\
               users_data=data_dict[1])

    else:
        filename=file.filename
        return render_template('layout.html', file_status="File %s not TXT!" % filename)
  
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)

