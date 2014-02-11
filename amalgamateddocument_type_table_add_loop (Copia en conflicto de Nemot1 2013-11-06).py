
#Note : OcrRecords from 1 to 1774 didn't have the Account Number inserted in the necessary
# Source_Bank_Account field

#####ALWAYS CHANGE THE LOT NUMBER IN THE LOOP TO THE ONE YOU WANT THEM TO BE ASSIGNED

# Lot0 <-> First 100 (Enersect) and from 101 to 600 (Assigned to Flatworld and Enersect and Enersect_Berlin) Total of 600
# Lot0 <-> From 101 to 600 (Flatworld) and  (Assigned to Flatworld,Enersect and Enersect_Berlin) Total of 500
# Lot0 <-> From 101 to 600 (Enersect_Berlin) Total of 500 (For Jonathan to duplicate)
# Lot1 <-> From 601 to 1100 (Assigned to FlatWorld) Total of 500
# Lot1 <-> From 1101 to 1110 (Assigned to FlatWorld) Total of 10
# Lot1 <-> From 1111 to 1150 (Assigned to FlatWorld) Total of 40
# Lot1 <-> From 1151 to 1300 (Assigned to FlatWorld) Total of 150
# Lot2 <-> From 1301 to 3300 (Assigned to Flatworld) Total of 2000
# Lot3 <-> From 3301 to 9000 (Assigned to Flatworld) Total of 5700
# Lot4 <-> From 9001 to 15343 (Assigned to FlatWorld) Total of 6342



#Enersect : 600

#FlatWorld : 14343

#Enersect_Berlin : 600 (+ 100 BLANK PROBABLES)

# Total of Lots Flatworld 100+500+500 = 1200

#####ALWAYS CHANGE THE LOT NUMBER IN THE LOOP TO THE ONE YOU WANT THEM TO BE ASSIGNED

##This are all the command necessary to copy the information in the .csv files to the
# SourcePdf table in the Database, assigned to the superuser "nemot"
# Most parameters can be modified, but need to find an existing recipient to succeed
# Example: Changing "nemot" to "Nathan" will only work if "Nathan" is a User already created in the Database


##### COPY ALL THIS INTO THE PYTHON SHELL, AFTER WRITING python manage.py shell


#Path to the .csv to be entered:

#csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/ChequeLIST.csv"
csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/albaraka2006.csv"
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


#Loading the SourcePdf data;; Make sure there are no white lines in the csv

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=',')

sourcelist_added = []

new_sourcepdf=""
counter = 0

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 20000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 1

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000



with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            print counter
            if counter <= num_files and counter > num_jump:
                #exists = SourcePdf.objects.filter(filename=row[1]).exists()
                #if exists == False:
                new_sourcepdf=SourcePdf()
                new_sourcepdf.job_directory=row[0]
                new_sourcepdf.filename=row[1].lower()
                new_sourcepdf.corrupt=row[2]
                new_sourcepdf.size=row[3]
                new_sourcepdf.multipart=row[4]
                new_sourcepdf.multipart_num_total=row[5]
                new_sourcepdf.multipart_filename=row[6]
                new_sourcepdf.document_type=row[7]
                
                doctype = SourceDocType.objects.get(name = row[7])
                new_sourcepdf.modified_document_type = doctype
                
                new_sourcepdf.Day=row[8]
                new_sourcepdf.Month=row[9]
                new_sourcepdf.Year=row[10]
                new_sourcepdf.FullDate=row[11]
                new_sourcepdf.Currency=row[12]
                
                new_sourcepdf.save()
                if(counter % 100 == 0):
                    print counter
                sourcelist_added.append(new_sourcepdf)


                
superuser = User.objects.get(username="nemot")
none_user = User.objects.get(username="None")

super_company = superuser.groups.all()[0]
#enersect_company = Group.objects.get(name="Enersect")
#enersect_berlin_company = Group.objects.get(name="Enersect")
#flatworld_company = Group.objects.get(name="FlatWorld")


with transaction.commit_on_success():
    for source in sourcelist_added:
        if source:
            
            #Change the Lot Number if it is not the first time that data is processed
            tohandle = SourcePdfToHandle(assignedcompany=super_company,assigneduser=superuser,lot_number=-1)
            #tohandle_enersect = SourcePdfToHandle(assignedcompany=enersect_company,assigneduser=none_user,lot_number=0)
            #tohandle_flatworld = SourcePdfToHandle(assignedcompany=flatworld_company,assigneduser=none_user,lot_number=-1)
            tohandle.save()
            #tohandle_enersect.save()
            #tohandle_flatworld.save()
            source.assigndata.add(tohandle)
            if(source.id % 100 == 0):
                    print source.id
            source.save()
            
            

            
from django.db.models import Count

duplicates = SourcePdf.objects.values('filename').annotate(count=Count('id')).order_by().filter(count__gt=1)

total_dupes = duplicates.count()

if total_dupes == 0:
    print "SUCCESS! NO DUPLICATES!"
    
else:
    for item in duplicates:
        this = SourcePdf.objects.filter(filename=item['filename'])
        print this
    #print SourcePdf.objects.filter(filename__in=[item['filename'] for item in duplicates])


####Get not Audited records for Re-Entry

user_company = Group.objects.get(name="FlatWorld")

all_flatworld = PdfRecord.objects.filter(sourcedoc_link__assigndata__assignedcompany = user_company)
the_user = User.objects.get(username="nemot")

count = 0
untouched_count = 0
touched_count = 0
            
with transaction.commit_on_success():

    for item in all_flatworld:
    
        if count < 200000:
            latest_entry = all_flatworld.filter(sourcedoc_link__assigndata__assignedcompany = user_company,sourcedoc_link = item.sourcedoc_link).latest('modification_date')
            
            if latest_entry:
            
                if latest_entry.audit_mark == "auditmarked_as_correct" or latest_entry.audit_mark == "duplicatemarked_reentered" or latest_entry.audit_mark_saved == "save_audited_entry" or latest_entry.audit_mark=="auditmarked_as_correct" or latest_entry.audit_mark == "auditmarked_confirmed_reassignment":
                    touched_count += 1
                    print "TOUCHED"
                else:
                    untouched_count += 1
                    print "UNTOUCHED"
                    
                    to_reassign_handles = latest_entry.sourcedoc_link.assigndata.filter(assignedcompany=user_company)
                            
                    for handle in to_reassign_handles:
                            
                        handle.checked = "unchecked"
                        handle.save()
                            
                        
                    memo_report = "Automatically re-assign by intelligent process in Pair Audit for being an untouched record. This being PK."+str(latest_entry.pk)+".Previous mark was:"+latest_entry.audit_mark
                    latest_entry.audit_mark = "auditmarked_confirmed_reassignment"
                    latest_entry.save()
                    report = Report(report_type="Audit",report_subtype="pair_audit_auto_reassign",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                    report.save()
                    
            count += 1
            print count
            
            