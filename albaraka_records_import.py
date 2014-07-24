###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/updatedTransactionFiles/AlbarakaBankStatements.csv"
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


#00.AlbarakaIndex,01.Transaction Index,02.Bank Account,03.Bank Name,04.Bank Currency,05.Post Day,06.Post Month,07.Post Year,
#08.Libelle,09.Reference,10.Value Day,11.Value Month,12.Value Year,13.Amount,14.Description,15.Transaction Id,
#16.libdesc,17.reftran,18.Provenance

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                new_legend = BankRecord.objects.get(BankRecordIndex = int(row[0]))
                try:
                    if len(row[1]):
                        try:
                            new_legend.TransactionIndex = row[1]
                        except:
                            filler = 0
                    if len(row[2]):
                        try:
                            new_legend.BankAccount = row[2]
                        except:
                            filler = 0
                    if len(row[3]):
                        try:
                            new_legend.BankName = row[3]
                        except:
                            filler = 0
                    if len(row[4]):
                        try:
                            new_legend.BankCurrency = row[4]
                        except:
                            filler = 0
                    if len(row[5]):
                        try:
                            new_legend.PostDay = row[5]
                        except:
                            filler = 0          
                    if len(row[6]):
                        try:
                            new_legend.PostMonth = row[6]
                        except:
                            filler = 0   
                    if len(row[7]):
                        try:
                            new_legend.PostYear = row[7]
                        except:
                            filler = 0   
                    if len(row[8]):
                        try:
                            new_legend.Libelle = row[8]
                        except:
                            filler = 0   
                    if len(row[9]):
                        try:
                            new_legend.Reference = row[9] 
                        except:
                            filler = 0   
                    if len(row[10]):
                        try:
                            new_legend.ValueDay = row[10]
                        except:
                            filler = 0           
                    if len(row[11]):
                        try:
                            new_legend.ValueMonth = row[11]
                        except:
                            filler = 0           
                    if len(row[12]):
                        try:
                            new_legend.ValueYear = row[12]
                        except:
                            filler = 0           
                    if len(row[13]):
                        try:
                            new_legend.Amount = row[13]
                        except:
                            filler = 0   
                    if len(row[14]):
                        try:
                            new_legend.Description = row[14]
                        except:
                            filler = 0   
                    if len(row[15]):
                        try:
                            new_legend.TransactionId = row[15]
                        except:
                            filler = 0    
                    if len(row[16]):
                        try:
                            new_legend.Libdesc = row[16]
                        except:
                            filler = 0  
                    if len(row[17]):
                        try:
                            new_legend.Reftran = row[17]
                        except:
                            filler = 0  
                    if len(row[18]):
                        try:
                            new_legend.Provenance = row[18]
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
            
        item.AffidavitString = affi_final
        item.save()