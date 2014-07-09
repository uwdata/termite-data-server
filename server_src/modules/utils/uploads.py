import csv
import os


SPREADSHEET_DIR = None
PLAINTEXT_DIR = None


def spreadsheet_dir(request):
    global SPREADSHEET_DIR
    if not SPREADSHEET_DIR:
        SPREADSHEET_DIR = os.path.join(request.folder, 'uploads', 'csv')
    return SPREADSHEET_DIR


def plaintext_dir(request):
    global PLAINTEXT_DIR
    if not PLAINTEXT_DIR:
        PLAINTEXT_DIR = os.path.join(request.folder, 'uploads', 'plaintext')
    return PLAINTEXT_DIR


def save_spreadsheet(request, name, ssheet):
    if not os.path.isdir(spreadsheet_dir(request)):
        os.makedirs(spreadsheet_dir(request))
    ss_fpath = os.path.join(spreadsheet_dir(request), name + '.csv')
    with open(ss_fpath, 'wb') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=ssheet[0], delimiter=",")
        writer.writeheader()
        for row in ssheet[1:]:
            writer.writerow(row)


def save_plaintext(request, name, ptext):
    if not os.path.isdir(plaintext_dir(request)):
        os.makedirs(plaintext_dir(request))
    pt_fpath = os.path.join(plaintext_dir(request), name + '.txt')
    with open(pt_fpath, 'wb') as outfile:
        outfile.write(ptext)

