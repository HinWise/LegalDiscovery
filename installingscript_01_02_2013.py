
#Reading the necessary CSVs. (In this case, we are reading the SourcePdf's with Document Types
#and CompanyOriginal rows

############ Need to modify info in this comment box ############
# Full path and name to your csv file
csv_filepathname_sourcepdfs="D:\Dropbox\NathanProject\NathanFixtures\BlankLIST.csv"
csv_filepathname_companyoriginals="D:\Dropbox\NathanProject\NathanFixtures\CompanyListNew.csv"
# Full path to the directory immediately above your django project directory
your_djangoproject_home="D:\Dropbox\NathanProject\ProjectFolder"
############ All you need to modify is above ############

import sys,os
sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] ='ProjectFolder.settings'

from enersectapp.models import *
from django.contrib.auth.models import User,Group,Permission
from django.db import transaction
from django.http import HttpResponse
import csv

#Loading the Internal Records (GrandeLivre)
#Make sure the name in the json "model" field is "enersectapp.InternalRecord"


###python manage.py loaddata InternalRecordData.json


#Loading the SourcePdf data;; Make sure there are no white lines in the csv

dataReader = csv.reader(open(csv_filepathname_sourcepdfs), delimiter='|')

new_sourcepdf="";
with transaction.commit_on_success():
    for row in dataReader:
        if row:
            new_sourcepdf=SourcePdf()
            new_sourcepdf.job_directory=row[0]
            new_sourcepdf.filename=row[1].lower()
            new_sourcepdf.document_type=row[2]
            new_sourcepdf.save()
            
#Loading the CompanyOriginal data;; Make sure there are no white lines in the csv

dataReader = csv.reader(open(csv_filepathname_companyoriginals), delimiter=',')

new_companyorig="";
with transaction.commit_on_success():
    for row in dataReader:
        if row:
            new_companyorig=CompanyOriginal()
            new_companyorig.ledgeryear_original=row[0]
            new_companyorig.accountnumber_original=row[1]
            new_companyorig.companyname_original=row[2]
            new_companyorig.save()


###python manage.py loaddata CompanyOriginal.json (Not there yet)



#Creating the filter keywords "all" and "pdf_all", necessary for the Linking Tool logic

filter = FilterSearchWords(pdf_searchword="all",pdf_filterword="pdf_all")
filter.save()

#Creating the interface links

##linkingui = UserInterfaceType(name="Linking Interface",redirection_url="linkui/spiderweb/")
##linkingui.save()

dataentryui = UserInterfaceType(name="Data Entry Interface",redirection_url="dataentryui/spider/")
dataentryui.save()


#Create ControlInternalRecord

controlintern = InternalRecord(Memo = "This is a Control Record")
controlintern.save()


#Creating the Records associated with those Internal Records

all_intern = InternalRecord.objects.all()

with transaction.commit_on_success():
    for item in all_intern:
        if item:
            rec = Record(internalrecord_link=item)
            if(item.id % 100 == 0):
                print item.id
            rec.save()



#Creating the ControlRecord

controlrecord = Record(name="ControlRecord", internalrecord_link=controlintern)
controlrecord.save()


#Entry Data TOOL is used, and that brings the OcrRecords, the related PdfRecords, and all
#the links of those PdfRecords: (Linked to ControlRecord, SourcePdF, OcrRecord, and CompanyTemplate 



#TO DO LIST:

#Creating the CompanyTemplate (List of meaningful Companies to be shown in Entry Data tool,
#as well as added from there. They are the original template (first instance) of a determined
#Company in the database, and all the variations will refer to it
#Example: Wooga is the CompanyTemplate, wooga corp.,woóga and Worga are variations of it
#It is possible that this variations are wrong, as they are "guesses", but it doesn't hurt to
#have it, as the original input is also saved.


#---> Temporarily, I'll just assume that every Company Original should be a Template as well.
#This is the code for that assumption:

all_template = CompanyOriginal.objects.all()

with transaction.commit_on_success():
    for item in all_template:
        if item:
            templa = CompanyTemplate(company_original=item,companyname_base=item.companyname_original)
            if(item.id % 100 == 0):
                print item.id
            templa.save()


#ControlCompanyOriginal

contr =CompanyOriginal(companyname_original="ControlCompanyOriginal")    
contr.save()        

#ControlCompanyTemplate

control =CompanyTemplate(company_original=contr,companyname_base="ControlCompanyTemplate")
control.save() 

            
#Creating the auth and users

superuser = User.objects.get(username="nemot")

all_permits = Permission.objects.filter(content_type__name="user").filter(content_type__name="source pdf").exclude(codename__icontains="delete")

new_group_super = Group(name="NathanTeam")
new_group_super.save()

new_group_super = Group.objects.get(name="NathanTeam")

superuser.groups.add(new_group_super)

superuser.save()


#super_profile = superuser.get_profile()
all_sources = SourcePdf.objects.all()
super_company = superuser.groups.all()[0]
super_name = superuser

with transaction.commit_on_success():
    for source in all_sources:
        if source:
            #super_profile.assignedsourcepdfs.add(source)
            tohandle = SourcePdfToHandle(assignedcompany=super_company,assigneduser=super_name)
            tohandle.save()
            source.assigndata.add(tohandle)
            if(source.id % 100 == 0):
                print source.id
            source.save()
            #super_profile.save()


            
new_group_invensis = Group(name="INVENSIS")
new_group_invensis.save()
new_group_invensis = Group.objects.get(name="INVENSIS")

new_group_leaders = Group(name="TeamLeaders")
new_group_leaders.save()
new_group_leaders = Group.objects.get(name="TeamLeaders")

new_group_leaders.permissions = all_permits

new_teamlead_invensis = User(username="InvensisTeamLead",password="invensisleadcool",is_active=True,is_staff=True)
new_teamlead_invensis.save()
new_teamlead_invensis = User.objects.get(username="InvensisTeamLead")

new_teamlead_invensis.groups.add(new_group_invensis)
new_teamlead_invensis.groups.add(new_group_leaders)

new_user_invensis = User(username="InvensisUser",password="invensisusercool",is_active=True,is_staff=True)
new_user_invensis.save()
new_teamlead_invensis = User.objects.get(username="InvensisUser")

new_user_invensis.groups.add(new_group_invensis)

new_user_invensis2 = User(username="InvensisUser2",password="invensisusercool",is_active=True,is_staff=True)
new_user_invensis2.save()
new_teamlead_invensis2 = User.objects.get(username="InvensisUser2")

new_user_invensis2.groups.add(new_group_invensis)


superuser.save()
new_group_invensis.save()
new_teamlead_invensis.save()
new_user_invensis.save()


#Profit!


#Bonus! Saving the list of Companies to a CSV file. This must be done each time a new CompanyTemplate is created.
## Only works from a View!

companytemplate_list = CompanyTemplate.objects.all().order_by('company_original__companyname_original')
    
companyname_list = []
    
response = HttpResponse(mimetype='text/csv')
response['Content-Disposition'] = 'attachment;filename="D:\Dropbox\NathanProject\NathanFixtures\CompanyTemplateList.csv"'
writer = csv.writer(response)


with transaction.commit_on_success():
    for i in companytemplate_list:
        writer.writerow([i.company_original.companyname_original])

return response
    
    

    
