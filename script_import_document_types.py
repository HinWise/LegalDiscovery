

#####ALWAYS CHANGE THE LOT NUMBER IN THE LOOP TO THE ONE YOU WANT THEM TO BE ASSIGNED

##### COPY ALL THIS INTO THE PYTHON SHELL, AFTER WRITING python manage.py shell


#Path to the .csv to be entered:

#csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/ChequeLIST.csv"
csv_filepathname_sourcepdfs="D:/Dropbox/NathanProject/NathanFixtures/SourcePdfs_Input/types.csv"
# Full path to the directory immediately above your django project directory
#your_djangoproject_home="/srv/enersectapp/app/ProjectFolder"
your_djangoproject_home="D:/Dropbox/NathanProject/ProjectFolder"


import sys,os
sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] ='ProjectFolder.settings'

from enersectapp.models import *
from django.contrib.auth.models import User,Group,Permission
from django.db import transaction
from django.http import HttpResponse
import csv


#Loading the SourcePdf data;; Make sure there are no white lines in the csv

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=',')

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            new_item = SourceDocType()
            new_item.name=row[0].lower()
            new_item.pretty_name=row[1]
            new_item.save()
            counter = counter+1
            print counter
            print new_item.name
            print new_item.pretty_name



            