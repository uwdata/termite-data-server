#!/usr/bin/env python
import os
import utils.uploads as uploads

def index():
    corpora = [fname[:-len(".csv")] for fname in os.listdir(uploads.spreadsheet_dir(request))]
    return {"corpora": corpora}
