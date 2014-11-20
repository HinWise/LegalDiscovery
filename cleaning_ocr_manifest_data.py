from enersectapp.models import *
from django.contrib.auth.models import User,Group,Permission
from django.db import transaction
import csv


piecenumberarray = ["03/05/2014","2010/00968","2126760 SP","3048686 SP","BL8549","Blank","CAN/005/2012","No","No piece number",
"Piece Number","SOL/CAN/007/2008","TMU-030407","Tunisia","v","yes","NO","Yes","no"]

ocr_matches = OcrRecord.objects.none()

for item in piecenumberarray:

    ocr_matches = ocr_matches | OcrRecord.objects.filter(Piece_Number = item)

ocr_matches = ocr_matches.distinct()    
    
with transaction.commit_on_success():
    for item in ocr_matches:
        item.Piece_Number = ""
        item.save()
        
src_matches = SourcePdf.objects.none()

for item in piecenumberarray:

    src_matches = src_matches | SourcePdf.objects.filter(Piece_NumberBeforeManifest = item)  
        
src_matches = src_matches.distinct() 

with transaction.commit_on_success():
    for item in src_matches:
        item.Piece_Number = ""
        item.Piece_NumberBeforeManifest = ""
        item.save()     

        

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/AffidavitManifestCurrencyCleanUp.csv"
# Full path to the directory immediately above your django project directory
#your_djangoproject_home="/srv/enersectapp/app/ProjectFolder"
your_djangoproject_home="C:/Dropbox/GitHub/LegalDiscovery/"

import sys,os
sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] ='ProjectFolder.settings'

from enersectapp.models import *
from django.contrib.auth.models import User,Group,Permission
from django.db import transaction
from django.http import HttpResponse
import csv
import string   

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=',')

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        original = row[0]
        substitute = row[1]
        
        all_ocr = OcrRecord.objects.filter(Currency = original)
        
        for item in all_ocr:
            item.Currency = substitute
            item.save()
            
        all_source = SourcePdf.objects.filter(CurrencyBeforeManifest = original)
        
        for source in all_source:
            source.Currency = substitute
            source.CurrencyBeforeManifest = substitute
            source.save()