#!/usr/bin/env python
import os
import utils.paths as paths

def index():
    corpus = request.vars['corpus']
    return {"csv": "/dataset/download/csv?corpus=" + corpus + ".csv",
            "ptext": "/dataset/download/plaintext?corpus=" +  corpus + ".txt"}

def csv():
    corpus = request.vars['corpus']
    with open(os.path.join(paths.spreadsheet(request), corpus)) as f:
        return f.read()

def plaintext():
    corpus = request.vars['corpus']
    with open(os.path.join(paths.plaintext(request), corpus)) as f:
        return f.read()
