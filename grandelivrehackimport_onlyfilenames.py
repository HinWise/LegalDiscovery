###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/MatchedGrandeLivreHack.csv"
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