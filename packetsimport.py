###Importing the Grande Livre Hack Information

csv_filepathname_sourcepdfs="C:/Dropbox/GitHub/LegalDiscovery/databases/Packets.csv"
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


#00.PacketLabel	01.MultipartFilenameStub	02.NumPackets	
#03.MaxPages	04.Description	05.From page	06.To page

counter = 0

with transaction.commit_on_success():
    for row in dataReader:
        if row:
            counter = counter+1
            if counter % 100 == 0:
                print counter
            if counter <= num_files and counter > num_jump:
                new_packet = Packet()
                try:
                    if len(row[0]):
                        try:
                            new_packet.PacketLabel = row[0]
                        except:
                            filler = 0
                    if len(row[1]):
                        try:
                            new_packet.MultipartFilenameStub = row[1]
                        except:
                            filler = 0
                    if len(row[2]):
                        try:
                            new_packet.NumPackets = row[2]
                        except:
                            filler = 0
                    if len(row[3]):
                        try:
                            new_packet.MaxPages = row[3]
                        except:
                            filler = 0
                    if len(row[4]):
                        try:
                            new_packet.Description = row[4]
                        except:
                            filler = 0          
                    if len(row[5]):
                        try:
                            new_packet.FromPage = row[5]
                        except:
                            filler = 0
                    if len(row[6]):
                        try:
                            new_packet.ToPage = row[6]
                        except:
                            filler = 0
                                            
                    new_packet.save()
                except:
                    print "SCHEISSE! --> "+row[0]+ " <----"
                    print row[0]
                    print "SCHEISSE ROW! --> "+str(counter) + " <----"