#!/usr/bin/env python
import os
import utils.uploads as uploads

def index():
    corpus = request.vars['corpus']
    return {"csv": "/dataset/download/csv?corpus=" + corpus + ".csv",
            "ptext": "/dataset/download/plaintext?corpus=" +  corpus + ".txt"}

def csv():
    corpus = request.vars['corpus']
    with open(os.path.join(uploads.spreadsheet_dir(request), corpus)) as f:
        return f.read()

def plaintext():
    corpus = request.vars['corpus']
    with open(os.path.join(uploads.plaintext_dir(request), corpus)) as f:
        return f.read()
