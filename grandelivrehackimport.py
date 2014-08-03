###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/MatchedGrandeLivre.csv"
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


#00.GrandeLivreIndex	01.BestMatch	02.Time Discrepancy	03.Debit	04.Credit	05.MEDollars	06.MECheqnum
#07.Day	08.Month	09.Year 10.Company	11.Memo	12.MECategory	13.MEPounds	14.MEEuros	15.MEFactnum	16.Accountnum
#17.MvtNo	18.PieceNo	19.Ledgeryear	20.MEDate	21.MECutoff	22.Journal	23.Lett	24.S	25.Exchange Rate	
#26.Bank Entry	27.Bank Account	28.Bank Name	29.Bank Currency
#30.MELedgerpage	31.MELedgersize	32.Filename

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                coincident_internal = InternalRecord.objects.get(InternalRecordIndex = row[0])
                try:
                    if len(row[1]):
                        try:
                            coincident_internal.BestTransactionMatch = row[1]
                        except:
                            filler = 0
                    if len(row[2]):
                        try:
                            coincident_internal.DateDiscrepancy = row[2]
                        except:
                            coincident_internal.DateDiscrepancy = 0
                    try:
                        coincident_internal.Debit = row[3]
                    except:
                        coincident_internal.Debit = ""
                        print row[3]
                    try:
                        coincident_internal.Credit = row[4]
                    except:
                        coincident_internal.Credit = ""
                        print row[4]
                    try:
                        coincident_internal.MEDollars = row[5]
                    except:
                        coincident_internal.MEDollars = ""
                        print row[5]
                    try:
                        coincident_internal.MEChequenum = row[6]
                    except:
                        coincident_internal.MEChequenum = ""
                        print row[6]
                    try:
                        coincident_internal.Day = row[7]
                    except:
                        coincident_internal.Day = ""
                        print row[7]
                    try:
                        coincident_internal.Month = row[8]
                    except:
                        coincident_internal.Month = ""
                        print row[8]
                    try:
                        coincident_internal.Year = row[9]
                    except:
                        coincident_internal.Year = ""
                        print row[9]
                    try:
                        coincident_internal.Company = row[10]
                    except:
                        coincident_internal.Company = ""
                        print row[10]
                    try:
                        coincident_internal.Memo = row[11]
                    except:
                        coincident_internal.Memo = ""
                        print row[11]
                    try:
                        coincident_internal.MECategory = row[12]
                    except:
                        coincident_internal.MECategory = "" 
                        print row[12]                        
                    try:
                        coincident_internal.MEPounds = row[13]
                    except:
                        coincident_internal.MEPounds = "" 
                        print row[13]
                    try:
                        coincident_internal.MEEuros = row[14]
                    except:
                        coincident_internal.MEEuros = "" 
                        print row[14]
                    try:
                        coincident_internal.MEFactureNum = row[15]
                    except:
                        coincident_internal.MEFactureNum = "" 
                        print row[15]
                    try:
                        coincident_internal.AccountNum = row[16]
                    except:
                        coincident_internal.AccountNum = "" 
                        print row[16]
                    try:
                        coincident_internal.NoMvt = row[17]
                    except:
                        coincident_internal.NoMvt = "" 
                        print row[17]
                    try:
                        coincident_internal.NoPiece = row[18]
                    except:
                        coincident_internal.NoPiece = "" 
                        print row[18]
                    try:
                        coincident_internal.LedgerYear = row[19]
                    except:
                        coincident_internal.LedgerYear = "" 
                        print row[19] 
                    try:
                        coincident_internal.MEDate = row[20]
                    except:
                        coincident_internal.MEDate = "" 
                        print row[20]
                    try:
                        coincident_internal.MECutoff = row[21]
                    except:
                        coincident_internal.MECutoff = "" 
                        print row[21]
                    try:
                        coincident_internal.Journal = row[22]
                    except:
                        coincident_internal.Journal = "" 
                        print row[22]
                    try:
                        coincident_internal.Lett = row[23]
                    except:
                        coincident_internal.Lett = ""   
                        print row[23]
                    try:
                        coincident_internal.S = row[24]
                    except:
                        coincident_internal.S = ""
                        print row[24]
                    try:
                        coincident_internal.ExchangeRate = row[25]
                    except:
                        coincident_internal.ExchangeRate = ""
                        print row[25]
                    try:
                        coincident_internal.BankEntry = row[26]
                    except:
                        coincident_internal.BankEntry = ""
                        print row[26]
                    try:
                        coincident_internal.BankAccount = row[27]
                    except:
                        coincident_internal.BankAccount = ""
                        print row[27]
                    try:
                        coincident_internal.BankName = row[28]
                    except:
                        coincident_internal.BankName = ""
                        print row[28]
                    try:
                        coincident_internal.BankCurrency = row[29]
                    except:
                        coincident_internal.BankCurrency = ""
                        print row[29]
                    try:
                        coincident_internal.MELedgerPage = row[30]
                    except:
                        coincident_internal.MELedgerPage = ""
                        print row[30]
                    try:
                        coincident_internal.MELedgerSize = row[31]
                    except:
                        coincident_internal.MELedgerSize = ""
                        print row[31]                      
                    try:
                        coincident_internal.Filename = row[32]
                    except:
                        coincident_internal.Filename = "" 
                        print row[32]
                    coincident_internal.save()
                except:
                    print "SCHEISSE! --> "+str(coincident_internal.pk) + " <----"
                    print row[0]
                    print "SCHEISSE ROW! --> "+str(counter) + " <----"