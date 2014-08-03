###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/MatchedGrandeLivre.csv"
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
from django import db


counter = 0

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 20000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 1

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000

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
                db.reset_queries()
            if counter <= num_files and counter > num_jump:
                new_item = InternalRecord.objects.get(InternalRecordIndex=row[0])
                for column in range(len(row)):
                    row_value = str(row_dictionary[str(column)])
                    try:
                        if row_value == "GrandeLivreIndex":
                            new_item.InternalRecordIndex = int(row[column])
                        if row_value == "TransactionIndex":
                            if(row[column]):
                                new_item.BestTransactionMatch = int(row[column])
                        if row_value == "MECompany":   
                            new_item.Company = str(row[column])
                        if row_value == "MEMemo":  
                            new_item.Memo = str(row[column] ) 
                        if row_value == "MEUnmatchedMemo": 
                            new_item.MEUnmatchedMemo = str(row[column]) 
                        if row_value == "MEMatchedMemo": 
                            new_item.MEMatchedMemo = str(row[column])
                        if row_value == "MECategory": 
                            new_item.MECategory = str(row[column])
                        if row_value == "MEDebit": 
                            new_item.Debit = str(row[column])
                        if row_value == "MECredit": 
                            new_item.Credit = str(row[column])
                        if row_value == "MESourceCurrency": 
                            new_item.MECurrency = str(row[column])   
                        if row_value == "MESourceAmount": 
                            new_item.MESourceAmount = str(row[column])  
                        if row_value == "MEExchangeRate": 
                            new_item.ExchangeRate = str(row[column])
                        if row_value == "MEActualExchangeRate": 
                            new_item.MEActualExchangeRate = str(row[column])
                        if row_value == "MEExchangeRateMismatch": 
                            new_item.MEExchangeRateMistmatch = str(row[column])
                        if row_value == "MECheqnum": 
                            new_item.MEChequeNum = str(row[column])  
                        if row_value == "MEFactnum": 
                            new_item.MEFactureNum = str(row[column])  
                        if row_value == "MEAccountnum": 
                            new_item.AccountNum = str(row[column])
                        if row_value == "MEMvtNo": 
                            new_item.NoMvt = str(row[column])
                        if row_value == "MEPieceNo": 
                            new_item.NoPiece = str(row[column])   
                        if row_value == "MELedgeryear": 
                            new_item.MELedgeryear = str(row[column])  
                        if row_value == "MEDay": 
                            new_item.MEDay = str(row[column])
                        if row_value == "MEMonth": 
                            new_item.MEMonth = str(row[column])
                        if row_value == "MEYear": 
                            new_item.MEYear = str(row[column])
                        if row_value == "MEDate": 
                            new_item.MEDate = str(row[column])
                        if row_value == "MECutoff": 
                            new_item.MECutoff = str(row[column])
                        if row_value == "MECorrection": 
                            new_item.MECorrection = str(row[column])
                        if row_value == "MEJournal": 
                            new_item.Journal = str(row[column])
                        if row_value == "MELett": 
                            new_item.Lett = str(row[column])
                        if row_value == "MES": 
                            new_item.S = str(row[column])
                        if row_value == "MELedgerpage": 
                            new_item.MELedgerPage = str(row[column])
                        if row_value == "MELedgersize": 
                            new_item.MELedgerSize = str(row[column])
                        if row_value == "Filename": 
                            new_item.Filename = str(row[column])
                        if row_value == "Materials": 
                            new_item.Materials = str(row[column])
                        if row_value == "MismatchAndNotCutoff": 
                            new_item.MismatchAndNotCutoff = str(row[column])
                        if row_value == "BankEntry": 
                            new_item.BankEntry = str(row[column])
                        if row_value == "BankAccount": 
                            new_item.BankAccount = str(row[column])
                        if row_value == "BankName": 
                            new_item.BankName = str(row[column])
                        if row_value == "BankCurrency": 
                            new_item.BankCurrency = str(row[column])
                    except:
                        print "<------"
                        print "BAD ROW -->"+str(row[0])+ "<---"
                        print "--------------------"
                        print "BAD VALUE -->"+row_value+ "<---"
                        print "------>"
                    new_item.save() 
