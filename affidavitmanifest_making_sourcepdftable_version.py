#00.Exhibit Number; 
#01.Document Type; 
#02.Document Date (Where existing); 
#03.Document Number (Where existing), 
#04.Beneficiary/Source/Author type of field (depending on the document type obviously. 
#These can be separate fields that we can filter down.); 
#05.Number of pages if multipage.
#You may also want to have a column that provides some sort of source-reference that would be useful 
#for locating the actual page.
#In fact, if you have a hard physical reference on the table, you don't need an exhibit number.
#[23/08/2014 19:53:42] nathan.williams.mba:  As long as I can give you that list back as:
#SRC___MXFTYJ4S_____element1_____000001, Exhibit A;
#and you can then feed those permanent numbers back into the system. 
#That will let me wiggle the list in excel with the lawyers, exhibit mark anything we want to disclose, 
#and then give you back the list so you can generate individual detail sources.

from enersectapp.models import *
from django.db import transaction
import csv

all_sources = SourcePdf.objects.all()

all_icr = all_sources.exclude(job_directory = "albaraka2006").exclude(job_directory = "albaraka2007")
all_icr_with_entry = all_icr.filter(pdfrecord__isnull = False)
all_albaraka = all_sources.filter(job_directory = "albaraka2006")|all_sources.filter(job_directory = "albaraka2007")|all_sources.filter(job_directory = "albarakabankstatements")
all_albaraka = all_albaraka.distinct()
all_grandelivre = all_sources.filter(job_directory = "grandelivreglobale")
all_albarakasource = all_sources.filter(job_directory = "albarakasource")


# Loop for sources related to Albaraka Source, to input the data in    
from django import db

count = 0
 
with transaction.commit_on_success():
 for sourcepdf in all_albarakasource:
    
    count += 1
    
    if count % 500 == 0:
        #print count 
        db.reset_queries()   
   
    try:
        albarakasource_item = AlbarakaSource.objects.filter(ServerFilenames__icontains = sourcepdf.filename)[0]
        sourcepdf.Day = albarakasource_item.Day
        sourcepdf.Month = albarakasource_item.Month
        sourcepdf.Year = albarakasource_item.Year
        sourcepdf.FullDate = albarakasource_item.CompleteDate
        sourcepdf.Document_Type = albarakasource_item.Document_Type
        if albarakasource_item.Doc_ID_Num_Cheque:
            sourcepdf.Document_Number = albarakasource_item.Doc_ID_Num_Cheque
        else:
            sourcepdf.Document_Number = albarakasource_item.Doc_ID_Num_Invoice
        sourcepdf.Beneficiary = albarakasource_item.Beneficiary
        sourcepdf.Currency = albarakasource_item.Currency
        sourcepdf.Amount = albarakasource_item.Amount
        sourcepdf.corpus_type = "ALBSR"
        sourcepdf.save()
    except:
        equi = ""
        #print "nein"

from django import db


#Faster loop than the original to save the Icr Information into the SourcePdfs
    
all_pdf = PdfRecord.objects.all()
    
count = 0
 
with transaction.commit_on_success():
 for pdf_item in all_pdf:
    
    count += 1
    
    if count % 500 == 0:
        print count 
        db.reset_queries()
        
    ocr_item = pdf_item.ocrrecord_link
    sourcepdf = pdf_item.sourcedoc_link
    
    sourcepdf.document_type = pdf_item.modified_document_type.name
    sourcepdf.modified_document_type = pdf_item.modified_document_type
    sourcepdf.Day = ocr_item.Day
    sourcepdf.Month = ocr_item.Month
    sourcepdf.Year = ocr_item.Year
    sourcepdf.FullDate = ocr_item.IssueDate
    sourcepdf.Beneficiary = ocr_item.Company
    sourcepdf.Document_Number = ocr_item.Document_Number
    sourcepdf.Currency = ocr_item.Currency
    sourcepdf.Amount = ocr_item.Amount
    sourcepdf.Piece_Number = ocr_item.Piece_Number
    sourcepdf.corpus_type = "ICR"
    
    sourcepdf.save()
    
   
## Cleaning loop for the fields of the SourcePdf table, to make it cleaner for exporting

all_sources = SourcePdf.objects.all()
from django import db
count = 0
 
with transaction.commit_on_success():
 for sourcepdf in all_sources:
    count += 1
    
    if count % 500 == 0:
        print count 
        db.reset_queries()
    
    if "Field" in sourcepdf.document_type or "MISSING" in sourcepdf.document_type or "UNREADABLE" in sourcepdf.document_type or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.document_type = ""
    if "Field" in sourcepdf.Day or "MISSING" in sourcepdf.Day or "UNREADABLE" in sourcepdf.Day or "NaN" in sourcepdf.Day or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Day = "*"
    if "Field" in sourcepdf.Month or "MISSING" in sourcepdf.Month or "UNREADABLE" in sourcepdf.Month or "NaN" in sourcepdf.Month or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Month = "*"
    if "Field" in sourcepdf.Year or "MISSING" in sourcepdf.Year or "UNREADABLE" in sourcepdf.Year or "NaN" in sourcepdf.Year or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Year = "*"
    if "Field" in sourcepdf.FullDate or "MISSING" in sourcepdf.FullDate or "UNREADABLE" in sourcepdf.FullDate or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.FullDate = ""
    if "NaN" in sourcepdf.FullDate:
        sourcepdf.FullDate = sourcepdf.FullDate.replace("NaN","*")
    if "Field" in sourcepdf.Beneficiary or "MISSING" in sourcepdf.Beneficiary or "UNREADABLE" in sourcepdf.Beneficiary or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Beneficiary = ""
    if "Field" in sourcepdf.Document_Number or "MISSING" in sourcepdf.Document_Number or "UNREADABLE" in sourcepdf.Document_Number or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Document_Number = ""
    if "Field" in sourcepdf.Currency or "MISSING" in sourcepdf.Currency or "UNREADABLE" in sourcepdf.Currency or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Currency = ""
    if "Field" in sourcepdf.Amount or "MISSING" in sourcepdf.Amount or "UNREADABLE" in sourcepdf.Amount or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Amount = ""
    if "Field" in sourcepdf.Piece_Number or "MISSING" in sourcepdf.Piece_Number or "UNREADABLE" in sourcepdf.Piece_Number or "Blank" in sourcepdf.document_type or "blank" in sourcepdf.document_type:
        sourcepdf.Piece_Number = ""
    sourcepdf.save()
