

###########################################ALBARAKA BANK STATEMENTS


#csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/databases/AlbarakaBankStatements.csv"
csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/AlbarakaBankStatements.csv"
# Full path to the directory immediately above your django project directory
#your_djangoproject_home="/srv/enersectapp/app/ProjectFolder/"
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

num_files = 200000000

num_jump = 1

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
           
            if counter <= num_files and counter > num_jump:

                new_bank=BankRecord(BankRecordIndex = row[0])
 
                new_bank.TransactionIndex=row[1]
                new_bank.BankAccount=row[2]
                new_bank.BankName=row[3]
                new_bank.BankCurrency=row[4]
                new_bank.PostDay=row[5]
                new_bank.PostMonth=row[6]
                new_bank.PostYear=row[7]
                new_bank.ValueDay=row[8]
                new_bank.ValueMonth=row[9]
                new_bank.ValueYear=row[10]
                new_bank.Libelle=row[11]
                new_bank.Reference=row[12]
                new_bank.Amount=row[13]
                new_bank.Description=row[14]
                new_bank.TransactionId=row[15]
                new_bank.Libdesc=row[16]
                new_bank.Reftran=row[17]
                new_bank.Provenance=row[18]
                
                new_transaction.save()
                if(counter % 100 == 0):
                    print counter

###########################################MATCHED ALBARAKA

#csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/databases/AlbarakaBankStatements.csv"
csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/MatchedAlbaraka.csv"
# Full path to the directory immediately above your django project directory
#your_djangoproject_home="/srv/enersectapp/app/ProjectFolder/"
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

num_files = 2000000000

num_jump = 1

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
           
            if counter <= num_files and counter > num_jump:
                
                new_transaction=TransactionTable(TransactionIndex = row[0])
 
                new_transaction.BankRecordsListOriginalArray=row[1]
                new_transaction.NumberBankRecordIndexes=int(row[2])
                
                new_transaction.InternalRecordListOriginalArray=row[3]
                new_transaction.NumberInternalRecordIndexes=int(row[4])
                
                new_transaction.DateDiscrepancy=int(row[5])
                new_transaction.Amount=row[6]
                new_transaction.AmountDiscrepancy=0
                new_transaction.PostDay=row[8]
                new_transaction.PostMonth=row[9]
                new_transaction.PostYear=row[10]
                new_transaction.ValueDay=row[11]
                new_transaction.ValueMonth=row[12]
                new_transaction.ValueYear=row[13]
                new_transaction.Libdesc=row[14]
                new_transaction.Reftran=row[15]
                new_transaction.BankAccount=row[16]
                new_transaction.BankName=row[17]
                new_transaction.BankCurrency=row[18]
                
                
                new_transaction.save()
                if(counter % 100 == 0):
                    print counter                    




#### TRANSACTION BANK RECORDS LIST

all_transactions = TransactionTable.objects.all()


for item in all_transactions:
    if item:
            
        clean_string = str(item.BankRecordsListOriginalArray).replace("[","").replace("]","")
        split_string = clean_string.split(",")
        
        if split_string != "":
            for transaction in split_string:
                
                try:
                    selected_bank = BankRecord.objects.get(BankRecordIndex = int(transaction))
                    item.bank_records_list.add(selected_bank)
                except:
                    print item.pk
                    