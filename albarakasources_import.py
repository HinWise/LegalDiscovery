###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/AlbarakaBeneficiaryMatchable.csv"
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



counter = 0

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 20000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 1

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000


#00.AlbarakaSourceIndex	01.Page(s)	02.FirstPage	03.Doc_Type	04.Doc_ID_Num_Cheque 05.Doc_ID_Num_Invoice	
#06.Beneficiary	07.Day	08.Month	09.Year	10.FullDate	11.StringAmount	12.Currency	13.Description	
#14.Page_Marking	15.Signed_By	16.File	17.Flagged	18.Entered_By	19.Uniform_File	20.NetAmount

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
                new_item = AlbarakaSource(AlbarakaSourceIndex=0)
                new_item.save()
                for column in range(len(row)):
                    
                    row_value = str(row_dictionary[str(column)])
                    print "<------"
                    print "ROW -->"+str(row[0])+ "<---"
                    print "--------------------"
                    print "VALUE -->"+row_value+ "<---"
                    print "------>"
                    try:
                        if row_value == "AlbarakaSourceIndex":
                            new_item.AlbarakaSourceIndex = int(row[column])
                        if row_value == "Page(s)":
                            new_item.PagesOriginalArrayString = str(row[column])
                        if row_value == "FirstPage":   
                            new_item.FirstPage = str(row[column])
                        if row_value == "Doc_Type":  
                            new_item.Document_Type = str(row[column] ) 
                        if row_value == "Doc_ID_Num_Cheque": 
                            new_item.Doc_ID_Num_Cheque = str(row[column]) 
                        if row_value == "Doc_ID_Num_Invoice": 
                            new_item.Doc_ID_Num_Invoice = str(row[column])
                        if row_value == "Beneficiary": 
                            new_item.Beneficiary = str(row[column])
                        if row_value == "Day": 
                            new_item.Day = str(row[column])   
                        if row_value == "Month": 
                            new_item.Month = str(row[column])  
                        if row_value == "Year": 
                            new_item.Year = str(row[column])
                        if row_value == "FullDate": 
                            new_item.CompleteDate = str(row[column])
                        if row_value == "StringAmount": 
                            new_item.StringAmount = str(row[column])
                        if row_value == "Currency": 
                            new_item.Currency = str(row[column])  
                        if row_value == "Description": 
                            new_item.Description = str(row[column])  
                        if row_value == "Page_Marking": 
                            new_item.PageMarking = str(row[column])
                        if row_value == "Signed_By": 
                            new_item.Signed_By = str(row[column])
                        if row_value == "File": 
                            new_item.FilenameUnclean = str(row[column])   
                        if row_value == "Flagged": 
                            new_item.Flagged = str(row[column])  
                        if row_value == "Entered_By": 
                            new_item.Entered_By = str(row[column])
                        if row_value == "Uniform_File": 
                            new_item.Filename = str(row[column])
                        if row_value == "NetAmount": 
                            new_item.Amount = str(row[column])
                    except:
                        print "<------"
                        print "BAD ROW -->"+str(row[0])+ "<---"
                        print "--------------------"
                        print "BAD VALUE -->"+row_value+ "<---"
                        print "------>"
                    new_item.save()    