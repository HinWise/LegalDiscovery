###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/TransactionsWithALB.csv"
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

with transaction.commit_on_success():
    for item in TransactionTable.objects.all():
        item.delete()


#0.TransactionIndex	1.IcrRecordIndex	2.NumIcrRecordIndices	3.AlbarakaIndex	
#4.Number of ALB Indexes	5.GrandeLivreIndex	6.Number of GL Indexes	
#7.Date Discrepancy	8.Amount	9.Amount Discrepancy	10.Post Day	11.Post Month	12.Post Year	13.Value Day	
#14.Value Month	15.Value Year	16.libdesc	17.reftran	18.Bank Account	19.Bank Name	20.Bank Currency	
#21.GL Memo	22.GL Company


row_dictionary = {}

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=';')

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if counter == 0:
            counter += 1
            for column in range(len(row)):
                print(row[column])
                row_dictionary[str(column)] = str(row[column])


dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=';')
                
counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                new_item = TransactionTable(TransactionIndex=0)
                new_item.save()
                for column in range(len(row)):
                    row_value = str(row_dictionary[str(column)])
                    try:
                        if row_value == "TransactionIndex":
                            new_item.TransactionIndex = int(row[column])
                        if row_value == "IcrRecordIndex":
                            new_item.OcrRecordListOriginalArray = str(row[column])
                        if row_value == "NumIcrRecordIndices":   
                            new_item.NumberOcrRecordIndexes = int(row[column])
                        if row_value == "AlbarakaIndex":  
                            new_item.BankRecordsListOriginalArray = str(row[column] ) 
                        if row_value == "Number of ALB Indexes": 
                            new_item.NumberBankRecordIndexes = int(row[column]) 
                        if row_value == "GrandeLivreIndex": 
                            new_item.InternalRecordListOriginalArray = str(row[column])
                        if row_value == "Number of GL Indexes": 
                            new_item.NumberInternalRecordIndexes = int(row[column])
                        if row_value == "ALBRecordIndex": 
                            new_item.AlbarakaSourceListOriginalArray = str(row[column])
                        if row_value == "NumALBRecordIndices": 
                            new_item.NumberAlbarakaSourceIndexes = int(row[column])
                        if row_value == "Date Discrepancy": 
                            new_item.DateDiscrepancy = int(row[column])   
                        if row_value == "Amount": 
                            new_item.Amount = str(row[column])  
                        if row_value == "Amount Discrepancy": 
                            new_item.AmountDiscrepancy = int(row[column])
                        if row_value == "Post Day": 
                            new_item.PostDay = str(row[column])
                        if row_value == "Post Month": 
                            new_item.PostMonth = str(row[column])
                        if row_value == "Post Year": 
                            new_item.PostYear = str(row[column])  
                        if row_value == "Value Day": 
                            new_item.ValueDay = str(row[column])  
                        if row_value == "Value Month": 
                            new_item.ValueMonth = str(row[column])
                        if row_value == "Value Year": 
                            new_item.ValueYear = str(row[column])
                        if row_value == "libdesc": 
                            new_item.Libdesc = str(row[column])   
                        if row_value == "reftran": 
                            new_item.Reftran = str(row[column])  
                        if row_value == "Bank Account": 
                            new_item.BankAccount = str(row[column])
                        if row_value == "Bank Name": 
                            new_item.BankName = str(row[column])
                        if row_value == "Bank Currency": 
                            new_item.BankCurrency = str(row[column])
                        if row_value == "GL Memo": 
                            new_item.GLMemo = str(row[column])
                        if row_value == "GL Company": 
                            new_item.GLCompany = str(row[column])
                    except:
                        print "<------"
                        print "BAD ROW -->"+str(row[0])+ "<---"
                        print "--------------------"
                        print "BAD VALUE -->"+row_value+ "<---"
                        print "------>"
                    new_item.save() 




from enersectapp.models import *
from django.db import transaction
import string

#Fill the CompleteDate fields in Transactions

counter = 0
                    
with transaction.commit_on_success():
    for transaction_item in TransactionTable.objects.all():
        transaction_item.CompleteValueDate = transaction_item.ValueDay+"/"+transaction_item.ValueMonth+"/"+transaction_item.ValueYear
        transaction_item.CompletePostDate = transaction_item.PostDay+"/"+transaction_item.PostMonth+"/"+transaction_item.PostYear
        transaction_item.save()
 

#Fill the ManyToMany field for Bank Records (Albarakas)
 
counter = 0
                    
with transaction.commit_on_success():
    for transaction_item in TransactionTable.objects.all():
        counter = counter+1
        if counter % 100 == 0:
            print counter
        if len(transaction_item.BankRecordsListOriginalArray) > 0:
            clean_string = transaction_item.BankRecordsListOriginalArray.replace("[","").replace("]","")
            splitted_items = clean_string.split(",")
            for item in splitted_items:
                try:
                    catched_item = BankRecord.objects.get(BankRecordIndex = int(item))
                    transaction_item.bank_records_list.add(catched_item)
                except:
                    print "-------->UNCATCHED BANK RECORD INDEX--> "+item+" <------"
 

#Fill the ManyToMany field for Internal Records (Grandelivres)
 
counter = 0
                    
with transaction.commit_on_success():
    for transaction_item in TransactionTable.objects.all():
        counter = counter+1
        if counter % 100 == 0:
            print counter                   
        if len(transaction_item.InternalRecordListOriginalArray) > 0 and transaction_item.InternalRecordListOriginalArray != "[]":
            clean_string = transaction_item.InternalRecordListOriginalArray.replace("[","").replace("]","")
            splitted_items = clean_string.split(",")
            for item in splitted_items:
                try:
                    catched_item = InternalRecord.objects.get(InternalRecordIndex = int(item))
                    transaction_item.internal_records_list.add(catched_item)
                except:
                    print "-------->UNCATCHED INTERNAL RECORD INDEX--> "+item+" <------"      


#Fill the ManyToMany field for Albaraka Source Records
                    
counter = 0
                    
with transaction.commit_on_success():
    for transaction_item in TransactionTable.objects.all():
        counter = counter+1
        if counter % 100 == 0:
            print counter                    
        if len(transaction_item.AlbarakaSourceListOriginalArray) > 0:
            clean_string = transaction_item.AlbarakaSourceListOriginalArray.replace("[","").replace("]","")
            splitted_items = clean_string.split(",")
            for item in splitted_items:
                try:
                    catched_item = AlbarakaSource.objects.get(AlbarakaSourceIndex = int(item))
                    transaction_item.albarakasource_records_list.add(catched_item)
                except:
                    print "-------->UNCATCHED ALBARAKA SOURCE RECORD INDEX--> "+item+" <------"

#Fill the ManyToMany field for Icr Records (Ocr)
                    
counter = 0
                    
with transaction.commit_on_success():
    for transaction_item in TransactionTable.objects.all()[:500]:
        counter = counter+1
        if counter % 100 == 0:
            print counter                    
        if len(transaction_item.OcrRecordListOriginalArray) > 0:
            clean_string = transaction_item.OcrRecordListOriginalArray.replace("[","").replace("]","")
            splitted_items = clean_string.split(",")
            for item in splitted_items:
                try:
                    catched_item = OcrRecord.objects.get(OcrRecordIndex = int(item))
                    transaction_item.ocr_records_list.add(catched_item)
                except:
                    print "-------->UNCATCHED OCR RECORD INDEX--> "+item+" <------"
                    
                    
                    
