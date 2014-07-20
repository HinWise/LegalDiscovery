from enersectapp.models import *
from django.db import transaction

#First, deletion of extra tables:
###

## First, Delete all duplicatemarked_reentered (Extra entries that are not useful for the final showing)

duplicatemarked = PdfRecord.objects.filter(audit_mark = "duplicatemarked_reentered")

count = 1

with transaction.commit_on_success():
    for duplicate in duplicatemarked:
        
        print "---> " +str(count)
        
        duplicate.delete()
        
        count +=1 
        
 

#Then, we find out what sourcedocs are repeated in more than one pdf_entry

from django.db.models import Count
 
duplicate_sources = all_pdf.values('sourcedoc_link').annotate(count=Count('id')).order_by().filter(count__gt=1).values_list('sourcedoc_link',flat=True).distinct()


#Second loop deletes the non-definitive entries from the database (duplicatemarked_reentered)
    
count = 1
    
with transaction.commit_on_success():
    for sourcedoc in duplicate_sources:
        
        print "---->" + str(count)
        
        sourcedoc_item = SourcePdf.objects.get(pk = sourcedoc)
        
        pdf_list = PdfRecord.objects.filter(sourcedoc_link = sourcedoc_item).order_by('modification_date')
        
        count += 1
        
        if len(pdf_list) > 1:
        
            old_records = pdf_list[:len(pdf_list)-1]
            
            for item in old_records:
            
                item.delete()

      
        
## Delete the Ocr Entries that don't have a Pdf Entry associated, as those weren't supossed to be there any way
## Deleting duplicate Ocr

from django.db import transaction
from enersectapp.models import *

all_ocr = OcrRecord.objects.all()
all_icr = PdfRecord.objects.all()

duplicated_ocr = OcrRecord.objects.exclude(pdfrecord__isnull = False)

count = 0

with transaction.commit_on_success():
    for item in duplicated_ocr:
        item.delete()
        count += 1
        print count


##Operations done after deletion of duplicates, in order:
        
#Making the Document Type of Ocr and Modified Document Type of Icr coincide

all_ocr = PdfRecord.objects.all()

with transaction.commit_on_success():
    for item in all_ocr:
        item.ocrrecord_link.Document_Type = item.modified_document_type.pretty_name
        item.ocrrecord_link.save()
        
#The objective of this file is to provide methods that will detect variations of "MISSING" and "UNREADABLE" and turn them into
#their proper forms.

#As well, in the second part of this files, there will be methods to clean Company Names, which are pretty dirty

from django.db import transaction
from enersectapp.models import *

## MISSING:

all_ocr = OcrRecord.objects.all()

###Lines to obtain the different variations of Missing:

#Line to visually compare the different variations:

all_ocr.filter(Receiver__icontains = "mis").values_list('Receiver',flat=True).distinct()
all_ocr.filter(Receiver__icontains = "unr").values_list('Receiver',flat=True).distinct()



###Lines to clean the selected fields:

#Currency

missing_currency = all_ocr.filter(Currency__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_currency:
        item.Currency = "MISSING"
        item.save()
        
unreadable_currency = all_ocr.filter(Currency__icontains = "unr")

with transaction.commit_on_success():
    for item in missing_currency:
        item.Currency = "UNREADABLE"
        item.save()

#Company

missing_company = all_ocr.filter(Company__icontains = "miss").exclude(Company__icontains = "MISSION")

with transaction.commit_on_success():
    for item in missing_company:
        item.Company = "MISSING NAME"
        item.save()        

unreadable_company = all_ocr.filter(Company__icontains = "unr").exclude(Company__icontains = "MISSION")

with transaction.commit_on_success():
    for item in unreadable_company:
        item.Company = "UNREADABLE NAME"
        item.save()           
        
#Address

missing_address = all_ocr.filter(Address__icontains = "miss").exclude(Address__icontains = "com").exclude(Address__icontains = "MISSISS").exclude(Address__icontains = "alb").exclude(Address__icontains = "transm")

with transaction.commit_on_success():
    for item in missing_address:
        item.Address = "MISSING"
        item.save()        

unreadable_address = all_ocr.filter(Address__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_address:
        item.Address = "UNREADABLE"
        item.save() 

#Telephone

missing_Telephone = all_ocr.filter(Telephone__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_Telephone:
        item.Telephone = "MISSING"
        item.save()        

unreadable_Telephone = all_ocr.filter(Telephone__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Telephone:
        item.Telephone = "UNREADABLE"
        item.save()   

#City

missing_City = all_ocr.filter(City__icontains = "miss").exclude(City__icontains = "misso").exclude(City__icontains = "ontario")

with transaction.commit_on_success():
    for item in missing_City:
        item.City = "MISSING"
        item.save()        

unreadable_City = all_ocr.filter(City__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_City:
        item.City = "UNREADABLE"
        item.save()           

#Country

missing_Country = all_ocr.filter(Country__icontains = "miss").exclude(Country__icontains = "ontario")

with transaction.commit_on_success():
    for item in missing_Country:
        item.Country = "MISSING"
        item.save()        

unreadable_Country = all_ocr.filter(Country__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Country:
        item.Country = "UNREADABLE"
        item.save()  

#IssueDate

with transaction.commit_on_success():
    for item in all_ocr.filter(IssueDate__icontains = "mis"):
        item.IssueDate = "NaN/NaN/Nan"
        item.save()


#Day, Month, Year

with transaction.commit_on_success():
    for item in all_ocr:
        if item.IssueDate.count('/') == 2:
            
            splitted_date = item.IssueDate.split('/')
            item.Day = splitted_date[0]
            item.Month = splitted_date[1]
            item.Year = splitted_date[2]
            item.save()
        if item.IssueDate == "Blank":
            item.Day = "Blank"
            item.Month = "Blank"
            item.Year = "Blank"
            item.save()
        if item.IssueDate == "NoIssueDateField":
            item.Day = "NoIssueDateDayField"
            item.Month = "NoIssueDateMonthField"
            item.Year = "NoIssueDateYearField"
            item.save()
  
#Day

with transaction.commit_on_success():
    for item in all_ocr.filter(Day = "00"):
        item.Day = "NaN"
        item.save()

#Month
        
with transaction.commit_on_success():
    for item in all_ocr.filter(Month = "00"):
        item.Month = "NaN"
        item.save()

#Year
        
with transaction.commit_on_success():
    for item in all_ocr.filter(Year = "Nan"):
        item.Year = "NaN"
        item.save()
        
##Middle of cleaning

#Document_Number

missing_Document_Number = all_ocr.filter(Document_Number__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_Document_Number:
        item.Document_Number = "MISSING"
        item.save()        

unreadable_Document_Number = all_ocr.filter(Document_Number__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Document_Number:
        item.Document_Number = "UNREADABLE"
        item.save() 

#PurchaseOrder_Number

missing_PurchaseOrder_Number = all_ocr.filter(PurchaseOrder_Number__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_PurchaseOrder_Number:
        item.PurchaseOrder_Number = "MISSING"
        item.save()        

unreadable_PurchaseOrder_Number = all_ocr.filter(PurchaseOrder_Number__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_PurchaseOrder_Number:
        item.PurchaseOrder_Number = "UNREADABLE"
        item.save() 

#Piece_Number

missing_Piece_Number = all_ocr.filter(Piece_Number__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_Piece_Number:
        item.Piece_Number = "MISSING"
        item.save()        

unreadable_Piece_Number = all_ocr.filter(Piece_Number__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Piece_Number:
        item.Piece_Number = "UNREADABLE"
        item.save()        

#Page_Number

missing_Page_Number = all_ocr.filter(Page_Number__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_Page_Number:
        item.Page_Number = "MISSING"
        item.save()        

unreadable_Page_Number = all_ocr.filter(Page_Number__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Page_Number:
        item.Page_Number = "UNREADABLE"
        item.save()         

        
with transaction.commit_on_success():
    for item in all_ocr.exclude(Page_Number = "Blank").exclude(Page_Number = "MISSING").exclude(Page_Number = "UNREADABLE").exclude(Page_Number = "NoPageNumberField"):
        item.Page_Number = str(int(item.Page_Number))
        item.save() 
        
#Notes

missing_Notes = all_ocr.filter(Notes__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_Notes:
        item.Notes = "MISSING"
        item.save()        

unreadable_Notes = all_ocr.filter(Notes__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Notes:
        item.Notes = "UNREADABLE"
        item.save()  
        
#Source_Bank_Account

missing_Source_Bank_Account = all_ocr.filter(Source_Bank_Account__icontains = "mis")

with transaction.commit_on_success():
    for item in missing_Source_Bank_Account:
        item.Source_Bank_Account = "MISSING"
        item.save()        

unreadable_Source_Bank_Account = all_ocr.filter(Source_Bank_Account__icontains = "unr")

with transaction.commit_on_success():
    for item in unreadable_Source_Bank_Account:
        item.Source_Bank_Account = "UNREADABLE"
        item.save() 
        

#########

#Company Field needs extra cleaning, both using marios's functions for cleaning utf-8 characters and checking anomalies visually

##(Executed Marios' function for cleaning, in file "accent_stripping_functions.py, function "strip_accents", with Company field in all_ocr

import re, unicodedata, string

from django.db import transaction
from enersectapp.models import *

#CSV List of all company names to get synonyms and such

import csv

b = open('companynames.csv', 'w')
a = csv.writer(b)

data = []

all_ocr = OcrRecord.objects.all()

with transaction.commit_on_success():
    for item in all_ocr.values('Company').distinct():
        try:
            data.append([str(item)])
        except:
            print "FUCK"
        
a.writerows(data)
b.close()

##Cleaning the "" symbol     

all_ocr = OcrRecord.objects.all()

with transaction.commit_on_success():
    for item in all_ocr:
        item.Company = item.Company.replace('"',"")
        item.save()

##

all_ocr = OcrRecord.objects.all()

all_thyna = all_ocr.filter(Company__icontains = "Thyna")

with transaction.commit_on_success():
    for item in all_thyna:
        item.Company = "TPS Thyna Petroleum Services"
        item.save()
    
all_estuhe = all_ocr.filter(Company__icontains = "ESTUHE")

with transaction.commit_on_success():
    for item in all_estuhe:
        item.Company = "HMUUESTUHE Tirstone"
        item.save()
        
all_enterprise_electricite = all_ocr.filter(Company__icontains = "inst").filter(Company__icontains = "tricit").exclude(Company__icontains = "hatab")

with transaction.commit_on_success():
    for item in all_enterprise_electricite:
        item.Company = "Enterprise d'Electricite et Climatisation Installation & Reparation"
        item.save()

        
all_lassiret_tijani = all_ocr.filter(Company__icontains = "lassiret").filter(Company__icontains = "bure")

with transaction.commit_on_success():
    for item in all_lassiret_tijani:
        item.Company = "Bureau d'Etude Lassiret Tijani"
        item.save()

all_fehmi = all_ocr.filter(Company__icontains = "fehmi")

with transaction.commit_on_success():
    for item in all_fehmi:
        item.Company = "Fehmi Mhiri Menuiserie Bois & Aluminium"
        item.save()        
 
all_westernpressure = all_ocr.filter(Company__icontains = "western").filter(Company__icontains = "pres")

with transaction.commit_on_success():
    for item in all_westernpressure:
        item.Company = "WPC Western Pressure Control LTD"
        item.save()
        
all_hammamet = all_ocr.filter(Company__icontains = "const").filter(Company__icontains = "bois")

with transaction.commit_on_success():
    for item in all_hammamet:
        item.Company = "STD D'Hammamet Materiaux Construction Bois & Quaincaillerie"
        item.save()   

all_questionmark = all_ocr.filter(Company__icontains = "?")

with transaction.commit_on_success():
    for item in all_questionmark:
        item.Company = "MISSING NAME"
        item.save()           
 
all_solidpetro = all_ocr.filter(Company__icontains = "solid").filter(Company__icontains = "serv").exclude(Company__icontains = "subsi").exclude(Company__icontains = "custo").exclude(Company__icontains = "SC").exclude(Company__icontains = "energ")

with transaction.commit_on_success():
    for item in all_solidpetro:
        item.Company = "NA Solid Petroserve LTD"
        item.save()

all_solidpetrosubsidiary= all_ocr.filter(Company__icontains = "solid").filter(Company__icontains = "serv").filter(Company__icontains = "subsidiar")

with transaction.commit_on_success():
    for item in all_solidpetrosubsidiary:
        item.Company = "A Subsidiary of NA Solid Petroserve LTD"
        item.save()

all_solidpetrocustomer = all_ocr.filter(Company__icontains = "solid").filter(Company__icontains = "serv").filter(Company__icontains = "customer")

with transaction.commit_on_success():
    for item in all_solidpetrocustomer:
        item.Company = "A Customer List of NA Solid Petroserve LTD"
        item.save()

all_solidenergy = all_ocr.filter(Company__icontains = "solid").filter(Company__icontains = "serv").filter(Company__contains = "energy")

with transaction.commit_on_success():
    for item in all_solidenergy:
        item.Company = "SOLID ENERGY SERVICES INC"
        item.save()

all_solidSC = all_ocr.filter(Company__icontains = "solid").filter(Company__icontains = "serv").filter(Company__contains = "SC")

with transaction.commit_on_success():
    for item in all_solidSC:
        item.Company = "SC SOLID PETROSERVE SRL"
        item.save()
        
 
def strip_accents(s): ## for alphanumeric input
    s = s.strip()
    s = re.sub(ur'\xa0', ' ', s) # non-breaking space -> space
    s = re.sub(ur'\u00b0', 'o', s,re.UNICODE) # degree -> o
    s = re.sub(ur'\u00a3', '(GBPOUNDS)', s,re.UNICODE) # £ -> (GBPOUNDS)   
    s = re.sub(ur'\x87', 'c', s,re.UNICODE) # ç -> c   
    s = re.sub(r'\x80', '(EUR)', s) # eurosymbol -> (EUR)
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn')
    return s.encode('utf-8')
    
count = 0

with transaction.commit_on_success():
    for item in all_ocr:
    
        print count
        print item.pk
        
        count +=1
        
        item.Address = strip_accents(item.Address)
        item.City = strip_accents(item.City)
        item.Country = strip_accents(item.Country)
        item.Company = strip_accents(item.Company)
        item.Currency = strip_accents(item.Currency)
        
        item.save()


        
###Importing the Company Name synonyms from a .csv that I wrote (around 9000 lines, "different" companies)

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/companynames_secondrow.csv"
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

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=',')

counter = 0

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 20000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 1

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                coincident_ocrs = OcrRecord.objects.filter(Company = row[1])
                for ocr_record in coincident_ocrs:
                    try:
                        ocr_record.CompanyLineIndexInteger = row[0]
                        ocr_record.OldCompanyLine = row[1]
                        ocr_record.Company = row[2]
                        ocr_record.save()
                    except:
                        print "SCHEISSE! --> "+str(ocr_record.pk) + " <----"
                        print row[0]
                        print "SCHEISSE ROW! --> "+str(counter) + " <----"
                    
            

