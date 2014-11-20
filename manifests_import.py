###Importing the Grande Livre Hack Information

#csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/albarakabankstatements.csv"
#csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/grandelivreglobale.csv"
csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/albarakasource.csv"
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



counter = 0

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 20000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 1

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000


#0.Directories	1.Filename	2.Corrupt	3.Size	
#4.Multipart	5.Outof	6.MultipartFilename
#7.Types	8.FileDate	9.Currency


row_dictionary = {}

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=',')

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if counter == 0:
            counter += 1
            for column in range(len(row)):
                print(row[column])
                row_dictionary[str(column)] = str(row[column])


dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=',')
                
counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                new_item = SourcePdf()
                new_item.save()
                for column in range(len(row)):
                    row_value = str(row_dictionary[str(column)])
                    try:
                        if row_value == "Directories":
                            new_item.job_directory = str(row[column])
                        if row_value == "Filename":
                            new_item.filename = str(row[column])
                        if row_value == "Corrupt":   
                            new_item.corrupt = str(row[column])
                        if row_value == "Size":  
                            new_item.size = str(row[column] ) 
                        if row_value == "Multipart": 
                            new_item.multipart = str(row[column]) 
                        if row_value == "Outof": 
                            new_item.multipart_num_total = str(row[column])
                        if row_value == "MultipartFilename": 
                            new_item.multipart_filename = str(row[column])
                        if row_value == "Types": 
                            new_item.document_type = str(row[column])
                        if row_value == "FileDate": 
                            new_item.FullDate = str(row[column])
                        if row_value == "Currency": 
                            new_item.Currency = str(row[column])   
                    except:
                        print "<------"
                        print "BAD ROW -->"+str(row[0])+ "<---"
                        print "--------------------"
                        print "BAD VALUE -->"+row_value+ "<---"
                        print "------>"
                    new_item.save() 

