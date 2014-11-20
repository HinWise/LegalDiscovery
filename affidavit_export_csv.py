##Data Dump of all the Corpuses in different .csvs

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

all_sources_not_first_albarakas = SourcePdf.objects.all().exclude(job_directory = "albaraka2006").exclude(job_directory = "albaraka2007").order_by('-job_directory').distinct()

documento = open("AffidavitManifest.csv", "wb")
csv_writer = csv.writer(documento) 
csv_writer.writerow(["SRCReference","Directories","Filename","Document Type","FullDate","Beneficiary","Document Number","Amount","Currency","Piece Number","MultipartNumber","OutOf","MultipartFilename"])

count = 0

with transaction.commit_on_success():
 for source in all_sources_not_first_albarakas:
 
    print count
    print source.pk
    count +=1 
    
    csv_writer.writerow([source.SourcePdfReference,source.job_directory,source.filename,source.document_type,source.FullDate,source.Beneficiary,
    source.Document_Number,source.Amount,source.Currency,source.Piece_Number,source.multipart,source.multipart_num_total,source.multipart_filename])

documento.close()
   
del csv_writer