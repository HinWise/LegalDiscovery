############ All you need to modify is in this comment box ############
# Full path and name to your csv file
csv_filepathname="D:\Dropbox\NathanProject\NathanFixtures\BlankLIST.csv"
# Full path to the directory immediately above your django project directory
your_djangoproject_home="D:\Dropbox\NathanProject\ProjectFolder"
############ All you need to modify is above ############


import sys,os
sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] ='ProjectFolder.settings'

from django.db import transaction
from docreader.models import Doctoread

import csv
dataReader = csv.reader(open(csv_filepathname), delimiter='|')

new_doc="";
with transaction.commit_on_success():
    for row in dataReader:
        new_doc=Doctoread()
        new_doc.job_directory=row[0]
        new_doc.filename=row[1]
        new_doc.label=row[2]
        new_doc.save()