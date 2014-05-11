
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response


from PyPDF2 import PdfFileWriter, PdfFileMerger, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import time
import tempfile

from django.db.models import Count

import json 

import time
import gc
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


import random


def test_function():

   
    
    title_string = "Liiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiine\n"
    interval = 2
    
    merger = PdfFileMerger()
    
    for i in range(10):
    
        if i % interval == 0:
            temp_filename = "tempdocument"+str(len(output_temp_documents_created))+".pdf"
            merger.write(temp_filename)
            output_temp_documents_created.append(temp_filename)
            
            merger = PdfFileMerger()
            
        print "---------> "+str(i)
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                    
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
      
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
        string_to_pdf(the_canvas,"---------> "+str(i) + title_string)
               
        the_canvas.save()
        
        input1 = PdfFileReader(tmpfile)
        
        merger.append(input1)

    merger.write("documenttest-output.pdf")
    

def string_to_pdf(canvas,string):

    splited_string = string.split("\n")
                            
    times = 0
    
    for item in splited_string:
        
        canvas.setFont("Helvetica", 11)
        canvas.drawString(2,800-(14*times),item)
        
        times +=1