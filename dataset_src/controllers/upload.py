#!/usr/bin/env python

import csv
import os
from db.Corpus_DB import Corpus_DB
import utils.uploads as uploads

def index():
    return {}

def generic_input(request, form, process_upload):
    flash = ""
    if form.accepts(request, session):
        ss_fname = form.vars.name + '.csv'
        ss_fpath = os.path.join(uploads.spreadsheet_dir(request), ss_fname)
        pt_fname = form.vars.name + '.txt'
        pt_fpath = os.path.join(uploads.plaintext_dir(request), pt_fname)
        if not os.path.isfile(ss_fpath) and not os.path.isfile(pt_fpath):
            ssheet, ptext = process_upload(form)
            uploads.save_spreadsheet(request, form.vars.name, ssheet)
            uploads.save_plaintext(request, form.vars.name, ptext)
            flash = "Submission successful."
        else:
            flash = "Corpus name in use. Please choose another"
    elif form.errors:
        flash = "There were errors in your submission."
    else:
        flash = "Please fill out the form"
    return {"form": form, "flash": flash}

def spreadsheet():
    def ImportSpreadsheet(dataset_id, spreadsheet_filename, is_csv=False, id_column='doc_id', content_column='doc_content'):
        dataset_path = '{}/data/{}'.format(request.folder, dataset_id)
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
        with Corpus_DB(path=dataset_path, isImport=True) as corpus_db:
            corpus_db.ImportFromSpreadsheet(spreadsheet_filename, is_csv=is_csv, id_key=id_column, content_key=content_column)
    DOC_ID_FIELD = "doc_id"
    DOC_CONTENT_FIELD = "doc_content"
    form = FORM(
            "Corpus name: ",
            INPUT(_name="name", _type="textarea", requires=IS_NOT_EMPTY()),
            "Document id field: ",
            INPUT(_name=DOC_ID_FIELD, value=DOC_ID_FIELD, _type="textarea", requires=IS_NOT_EMPTY()),
            "Document content field: ",
            INPUT(_name=DOC_CONTENT_FIELD, value=DOC_CONTENT_FIELD, _type="textarea", requires=IS_NOT_EMPTY()),
            "File: ",
            INPUT(_name="corpus", _type="file", requires=IS_NOT_EMPTY()),
            INPUT(_type="submit")
            )
    def process_upload(form):
        upload = form.vars.corpus.file
        ptext = []
        reader = csv.DictReader(upload, delimiter=",")
        field_map = {form.vars.doc_id: DOC_ID_FIELD, form.vars.doc_content: DOC_CONTENT_FIELD}
        ssheet = [[field_map[field] if field in field_map else field
                for field in reader.fieldnames]]
        for row in reader:
            ssheet.append(row)
            ptext.append("{} {}\n".format(row[DOC_ID_FIELD], row[DOC_CONTENT_FIELD]))
        return (ssheet, "".join(ptext))
    return generic_input(request, form, process_upload)

def plaintext():
    def ImportPlaintext(dataset_id, plaintext_filename):
        dataset_path = '{}/data/{}'.format(request.folder, dataset_id)
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
        with Corpus_DB(path=dataset_path, isImport=True) as corpus_db:
            corpus_db.ImportFromFile(plaintext_filename)
    form = FORM(
            "Corpus name: ",
            INPUT(_name="name", _type="textarea", requires=IS_NOT_EMPTY()),
            "Corpus (one document per line):",
            BR(),
            TEXTAREA(_name='corpus', value='', requires=IS_NOT_EMPTY()),
            INPUT(_type="submit")
            )
    def process_upload(form):
        upload = form.vars.corpus
        ptext = []
        ssheet = [["doc_id", "doc_content"]]
        for n, line in enumerate(upload.split("\n")):
            ptext.append(str(n) + " " + line.strip())
            ssheet.append({"doc_id": str(n),
                "doc_content": line.strip()})
        return (ssheet, "\n".join(ptext))
    return generic_input(request, form, process_upload)
