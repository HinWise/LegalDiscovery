
from enersectapp.models import *
from django.contrib.auth.models import User,Group,Permission
from django.db import transaction


###DELETING ALL INTERNAL RECORDS (GRANDE LIVRE) BEFORE ADDING THEM, BUT NOT THE TEST INTERNAL RECORD, AS EVERYTHING IS ASSOCIATED WITH IT

count = 0

all_internal = InternalRecord.objects.all()

all_internal.count()

all_internal = all_internal[1:20000]

with transaction.commit_on_success():
 for item in all_internal:
   print count
   count += 1
   item.delete()

###########################################ALBARAKA BANK STATEMENTS


csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/databases/AlbarakaBankStatements.csv"
#csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/AlbarakaBankStatements.csv"
# Full path to the directory immediately above your django project directory
your_djangoproject_home="/srv/enersectapp/app/ProjectFolder/"
#your_djangoproject_home="C:/Dropbox/GitHub/LegalDiscovery/"

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
                
                new_bank.save()
                if(counter % 100 == 0):
                    print counter


###########################################INTERNAL RECORD GRANDE LIVRE STATEMENTS


csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/databases/MatchedGrandeLivre.csv"
#csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/MatchedGrandeLivre.csv"
# Full path to the directory immediately above your django project directory
your_djangoproject_home="/srv/enersectapp/app/ProjectFolder/"
#your_djangoproject_home="C:/Dropbox/GitHub/LegalDiscovery/"

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

                new_internal=InternalRecord(InternalRecordIndex = int(row[0]))
 
                try:
                    new_internal.BestTransactionMatch=int(row[1])
                except:
                    missed = ""
                try:
                    new_internal.DateDiscrepancy=int(row[2])
                except:
                    missed = ""
                new_internal.Debit=row[3]
                new_internal.Credit=row[4]
                new_internal.MEDollars=row[5]
                new_internal.MEChequeNum=row[6]
                new_internal.Day=row[7]
                new_internal.Month=row[8]
                new_internal.Year=row[9]
                new_internal.Company=row[10]
                new_internal.Memo=row[11]
                new_internal.MECategory=row[12]
                new_internal.MEPounds=row[13]
                new_internal.MEEuros=row[14]
                new_internal.MEFactureNum=row[15]
                new_internal.AccountNum=row[16]
                new_internal.NoMvt=row[17]
                new_internal.NoPiece=row[18]
                new_internal.LedgerYear=row[19]
                new_internal.MEDate=row[20]
                new_internal.MECutoff=row[21]
                new_internal.Journal=row[22]
                new_internal.Lett=row[23]
                new_internal.S=row[24]
                new_internal.ExchangeRate=row[25]
                new_internal.ExistingBankEntry=row[26]
                new_internal.BankAccount=row[27]
                new_internal.BankName=row[28]
                new_internal.BankCurrency=row[29]
                
                new_internal.save()
                if(counter % 100 == 0):
                    print counter                    
                    
                    
###########################################MATCHED ALBARAKA / TRANSACTION TABLE

csv_filepathname_sourcepdfs="/srv/enersectapp/app/ProjectFolder/databases/MatchedAlbaraka.csv"
#csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/MatchedAlbaraka.csv"
# Full path to the directory immediately above your django project directory
your_djangoproject_home="/srv/enersectapp/app/ProjectFolder/"
#your_djangoproject_home="C:/Dropbox/GitHub/LegalDiscovery/"

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
                try:
                    new_transaction.NumberInternalRecordIndexes=int(row[4])
                except:
                    missed = ""
                
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




#### TRANSACTION BANK RECORDS FILLING

all_transactions = TransactionTable.objects.all()

counter = 0

with transaction.commit_on_success():
    for item in all_transactions:
    
        counter += 1
        print counter
        
        if item:
                
            clean_string_bank = str(item.BankRecordsListOriginalArray).replace("[","").replace("]","")
            split_string_bank = clean_string_bank.split(",")
            
            
            
            if split_string_bank != "":
                for transact in split_string_bank:
                    
                    try:
                        selected_bank = BankRecord.objects.get(BankRecordIndex = int(transact))
                        item.bank_records_list.add(selected_bank)
                    except:
                        print item.pk

#### TRANSACTION GRANDELIVRE LIST FILLING

all_transactions = TransactionTable.objects.all()

counter = 0

with transaction.commit_on_success():
    for item in all_transactions:
    
        counter += 1
        print counter
    
        if item:
                
            clean_string_internal = str(item.InternalRecordListOriginalArray).replace("[","").replace("]","")
            split_string_internal = clean_string_internal.split(",")
            
            
            if split_string_internal != "":
                for transact in split_string_internal:
                    
                    try:
                        selected_internal = InternalRecord.objects.get(InternalRecordIndex = int(transact))
                        item.internal_records_list.add(selected_internal)
                    except:
                        print item.pk                    