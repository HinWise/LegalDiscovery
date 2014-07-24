###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/ReferenceLegend_To_Import_NoLegend.csv"
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

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter=';')

counter = 0

#This is the number of rows from the csv you want to be entered, change the number accordingly
num_files = 20000000

#This is the number of rows that it will jumps before starting to introduce them, in case you introduced some of them before
num_jump = 1

#If you want to enter all the source pdfs rows from the csv, uncomment this next line
#num_files = 1000000000


#00.PacketLabel	01.MultipartFilenameStub	02.NumPackets	
#03.MaxPages	04.Description	05.From page	06.To page

TransactionLegend.objects.all().delete()

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                new_legend = TransactionLegend()
                try:
                    if len(row[0]):
                        try:
                            new_legend.ReferenceType = row[0]
                        except:
                            filler = 0
                    if len(row[1]):
                        try:
                            new_legend.StringNoException = row[1]
                        except:
                            filler = 0
                    if len(row[2]):
                        try:
                            new_legend.StringWithException = row[2]
                        except:
                            filler = 0
                    if len(row[3]):
                        try:
                            new_legend.IncludeListReferenceDocuments = row[3]
                        except:
                            filler = 0
                    if len(row[4]):
                        try:
                            new_legend.ConditionalRule = row[4]
                        except:
                            filler = 0          
                    
                    new_legend.save()
                except:
                    print "SCHEISSE! --> "+row[0]+ " <----"
                    print row[0]
                    print "SCHEISSE ROW! --> "+str(counter) + " <----"
                    
                    

### Function to change the Affidavit String Fields in the TransactionTable to its proper values                    
                    
from enersectapp.models import *
from django.db import transaction

count = 0

with transaction.commit_on_success():
    for item in TransactionTable.objects.all():
    
        if count%100 == 0:
            print count
        
        count += 1
        
        affi_date = ""
        affi_amount = ""
        affi_company = ""
        
        all_dates =  []
        all_dates.append(item.CompletePostDate)
        all_dates.append(item.CompleteValueDate)
        
        for internal in item.internal_records_list.all():
            all_dates.append(internal.Day+"/"+internal.Month+"/"+internal.Year)
        for bankrecord in item.bank_records_list.all():
            all_dates.append(bankrecord.ValueDay+"/"+bankrecord.ValueMonth+"/"+bankrecord.ValueYear)
            all_dates.append(bankrecord.PostDay+"/"+bankrecord.PostMonth+"/"+bankrecord.PostYear)
        
        if len(all_dates)>0:
            all_dates.sort(reverse=True)
            affi_date = all_dates[0]
            
        affi_amount = item.Amount + " " + item.BankCurrency
        
        print "----> "+item.Libdesc+" <-----"
        legend = TransactionLegend.objects.get(ReferenceType = item.Libdesc)
        
        
        affi_final = ""
        
        if legend.ConditionalRule == "No":
            
            affi_final = ""
            
        elif legend.ConditionalRule == "Yes":
        
            affi_final = legend.StringNoException
        
        elif legend.ConditionalRule == "Company":
        
            if affi_company != "":
            
                affi_final = legend.StringNoException
            else:
            
                affi_final = legend.StringWithException
                
        if "(1)" in affi_final:
        
            affi_final = affi_final.replace("(1)",affi_date)
            
        if "(2)" in affi_final:
        
            affi_final = affi_final.replace("(2)",affi_amount)
            
        if "(3)" in affi_final:
        
            affi_final = affi_final.replace("(3)",affi_company)
        
        if "(JUMP)" in affi_final:
        
            affi_final = affi_final.replace("(JUMP)","\n")

        
        item.AffidavitString = affi_final
        item.save()