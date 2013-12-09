
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
# Lot5 <-> From 15343 to 16437 + original 100 (Assigned to FlatWorld) Total of 1194



#Enersect : 600

#FlatWorld : 16437

#Enersect_Berlin : 600 (+ 100 BLANK PROBABLES)

# Total of Lots Flatworld 100+500+500 = 1200

#####ALWAYS CHANGE THE LOT NUMBER IN THE LOOP TO THE ONE YOU WANT THEM TO BE ASSIGNED

##This are all the command necessary to copy the information in the .csv files to the
# SourcePdf table in the Database, assigned to the superuser "nemot"
# Most parameters can be modified, but need to find an existing recipient to succeed
# Example: Changing "nemot" to "Nathan" will only work if "Nathan" is a User already created in the Database


##### COPY ALL THIS INTO THE PYTHON SHELL, AFTER WRITING python manage.py shell


#Path to the .csv to be entered:

csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/albaraka2006.csv"
#csv_filepathname_sourcepdfs="D:\Dropbox\NathanProject\NathanFixtures\SourcePdfs_Input\AmalgamatedDocument.csv"
# Full path to the directory immediately above your django project directory
your_djangoproject_home="/srv/enersectapp/app/ProjectFolder"
#your_djangoproject_home="D:/Dropbox/NathanProject/ProjectFolder"


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
counter = -1

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 2000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 0

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000

uncategorized_type = SourceDocType.objects.get(name="uncategorized")
none_user = User.objects.get(username="None")

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter <= num_files and counter > num_jump:
                new_sourcepdf=SourcePdf()
                new_sourcepdf.job_directory=row[0]
                new_sourcepdf.filename=row[1].lower()
                new_sourcepdf.document_type="uncategorized"
                new_sourcepdf.modified_document_type=uncategorized_type
                new_sourcepdf.modification_doctype_author=none_user
                new_sourcepdf.corrupt=row[2]
                new_sourcepdf.size=row[3]
                new_sourcepdf.multipart=row[4]
                new_sourcepdf.multipart_num_total=row[5]
                new_sourcepdf.multipart_filename=row[6]
                
                new_sourcepdf.save()
                print counter
                #sourcelist_added.append(new_sourcepdf)


                
superuser = User.objects.get(username="nemot")


super_company = superuser.groups.all()[0]
#enersect_company = Group.objects.get(name="Enersect")
#enersect_berlin_company = Group.objects.get(name="Enersect")
flatworld_company = Group.objects.get(name="FlatWorld")

#all_cheque = SourcePdf.objects.filter(modified_document_type__name = "cheque") | SourcePdf.objects.filter(modified_document_type__name="cheque stub")
#all_cheque_noflatworld = all_cheque.exclude(assigndata__assignedcompany = flatworld_company)

with transaction.commit_on_success():
    for source in sourcelist_added:
        if source:
            #Change the Lot Number if it is not the first time that data is processed
            #tohandle = SourcePdfToHandle(assignedcompany=super_company,assigneduser=superuser,lot_number=5)
            #tohandle_enersect = SourcePdfToHandle(assignedcompany=enersect_company,assigneduser=none_user,lot_number=0)
            tohandle_flatworld = SourcePdfToHandle(assignedcompany=flatworld_company,assigneduser=none_user,lot_number=5)
            #tohandle.save()
            #tohandle_enersect.save()
            tohandle_flatworld.save()
            source.assigndata.add(tohandle_flatworld)
            if(source.id % 10 == 0):
                print source.id
            source.save()
            

            
from django.db.models import Count

duplicates = SourcePdf.objects.values('filename').annotate(count=Count('id')).order_by().filter(count__gt=1)

duplicates_list = SourcePdf.objects.filter(filename=[item['filename'] for item in duplicates])

total_dupes = duplicates.count()

if total_dupes == 0:
    print "SUCCESS! NO DUPLICATES!"
    
else:
    print duplicates.count()
    '''for item in duplicates:
        test = SourcePdf.objects.filter(filename=item['filename'])
        print test.count()'''
    
'''

counter = 0

if total_dupes == 0:
    print "SUCCESS! NO DUPLICATES!"
  
else:
    with transaction.commit_on_success():
        for item in duplicates:
            counter = counter + 1
            test = SourcePdf.objects.filter(filename=item['filename'])
            if (len(test)) > 1:
                test = test[1]
                test.delete()
            if (counter % 100 ==0):
                print counter
            '''

counter = 0

with transaction.commit_on_success():            
    for item in SourcePdf.objects.values_list('filename', flat=True).distinct():
        counter = counter+1
        if (counter % 100 == 0):
            print counter
        if counter < 15000:
            SourcePdf.objects.filter(pk__in=SourcePdf.objects.filter(filename=item).values_list('id', flat=True)[1:]).delete()

            