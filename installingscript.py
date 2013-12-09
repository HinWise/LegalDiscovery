
#Loading the Internal Records
#Make sure the name in the json "model" field is "nathanapp.InternalRecord"

###python manage.py loaddata InternalRecordData.json


#Loading the OcrRecords
#Make sure the name in the json "model" field is "nathanapp.OcrRecord"

###python manage.py loaddata OcrRecordData.json

#Then copy and paste this script to the shell (python manage.py shell), press Enter a few times, and enjoy!

###python installingscript.py


from nathanapp.models import *
from django.db import transaction



#Creating the filter keywords "all" and "pdf_all"

filter = FilterSearchWords(pdf_searchword="all",pdf_filterword="pdf_all")
filter.save()

#Creating the interface links

linkingui = UserInterfaceType(name="Linking Interface",redirection_url="linkui/spiderweb/")
linkingui.save()

dataentryui = UserInterfaceType(name="Data Entry Interface",redirection_url="dataentryui/spider/")
dataentryui,save()


#Create ControlInternalRecord

controlintern = InternalRecord(Memo = "This is a Control Record")
controlintern.save()


#Creating the Records associated with those Internal Records

all_intern = InternalRecord.objects.all()

with transaction.commit_on_success():
    for item in all_intern:
        rec = Record(internalrecord_link=item)
        if(item.id % 100 == 0):
            print item.id
        rec.save()


#Creating the ControlRecord

controlrecord = Record(name="ControlRecord", internalrecord_link=controlintern)
controlrecord.save()


#Creating the PdfRecords associated with those OcrRecords and the ControlRecord (unless they are already linked)
#Remember to add here the PDF Viewer Data, where filename in PDF is the same as Doc_Name in Ocr

all_ocr = OcrRecord.objects.all()

with transaction.commit_on_success():
    for i in all_ocr:
        rec = PdfRecord(ocrrecord_link=i,record_link=controlrecord)
        if(i.id % 100 == 0):
            print i.id
        rec.save()


#Creating the auth?



#Profit!
