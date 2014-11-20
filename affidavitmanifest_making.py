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

#Loop for every SourcePdf related to Icr documents with entries.

count = 0
 
with transaction.commit_on_success():
 for sourcepdf in all_icr_with_entry:
    print count
    count += 1
    try:
        affidavit_item = AffidavitManifest.objects.get(SourcePdfLink = sourcepdf)
    except:
        affidavit_item = AffidavitManifest()  
        
    affidavit_item.SourcePdfLink = sourcepdf
    
    affidavit_item.corrupt = sourcepdf.corrupt
    affidavit_item.directory = sourcepdf.job_directory
    affidavit_item.filename = sourcepdf.filename
    affidavit_item.Document_Type = sourcepdf.document_type
    affidavit_item.modified_document_type = sourcepdf.modified_document_type
    affidavit_item.size = sourcepdf.size
    affidavit_item.multipart = sourcepdf.multipart
    affidavit_item.multipart_num_total = sourcepdf.multipart_num_total
    affidavit_item.multipart_filename = sourcepdf.multipart_filename
    affidavit_item.Day = sourcepdf.Day
    affidavit_item.Month = sourcepdf.Month
    affidavit_item.Year = sourcepdf.Year
    affidavit_item.FullDate = sourcepdf.FullDate
    affidavit_item.Currency = sourcepdf.Currency
    
    pdf_item = PdfRecord.objects.filter(sourcedoc_link = sourcepdf).order_by('-modification_date')[0]
    ocr_item = pdf_item.ocrrecord_link
    affidavit_item.OcrRecordLink = ocr_item
    affidavit_item.Document_Type = pdf_item.modified_document_type.name
    affidavit_item.modified_document_type = pdf_item.modified_document_type
    affidavit_item.Day = ocr_item.Day
    affidavit_item.Month = ocr_item.Month
    affidavit_item.Year = ocr_item.Year
    affidavit_item.FullDate = ocr_item.IssueDate
    affidavit_item.Beneficiary = ocr_item.Company
    affidavit_item.Document_Number = ocr_item.Document_Number
    affidavit_item.Currency = ocr_item.Currency
    affidavit_item.corpus_type = "ICR"
    
    affidavit_item.save()
    

    
    ##
    
    #Try to find a linked Icr to extract the data from, and if not, try to find other table
    try:
        pdf_item = PdfRecord.objects.get(sourcedoc_link = sourcepdf)
        ocr_item = pdf_item.ocrrecord_link
        affidavit_item.Document_Type = pdf_item.modified_document_type.name
        affidavit_item.modified_document_type = pdf_item.modified_document_type
        affidavit_item.Day = ocr_item.Day
        affidavit_item.Month = ocr_item.Month
        affidavit_item.Year = ocr_item.Year
        affidavit_item.FullDate = ocr_item.IssueDate
        affidavit_item.Beneficiary = ocr_item.Company
        affidavit_item.Document_Number = ocr_item.Document_Number
        affidavit_item.Currency = ocr_item.Currency
        affidavit_item.corpus_type = "ICR"
    except:
        #Try to get Albaraka Source
        try:
            albarakasource_item = AlbarakaSource.objects.get(Filename = sourcepdf.filename)
            affidavit_item.Day = albarakasource_item.Day
            affidavit_item.Month = albarakasource_item.Month
            affidavit_item.Year = albarakasource_item.Year
            affidavit_item.FullDate = albarakasource_item.CompleteDate
            affidavit_item.Document_Type = albarakasource_item.Document_Type
            if albarakasource_item.Doc_ID_Num_Cheque:
                affidavit_item.Document_Number = albarakasource_item.Doc_ID_Num_Cheque
            else:
                affidavit_item.Document_Number = albarakasource_item.Doc_ID_Num_Invoice
            affidavit_item.Beneficiary = albarakasource_item.Beneficiary
            affidavit_item.Currency = albarakasource_item.Currency
            affidavit_item.corpus_type = "ALBSR"
        except:
            print "nein"