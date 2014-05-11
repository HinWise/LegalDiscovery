
from PyPDF2 import PdfFileWriter, PdfFileMerger, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import time
import tempfile


import json 

import time
import gc


import datetime


import random


def test_function(interval_to,range_to):

   
    
    title_string = "Liiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiine\n"
    
    
    merger = PdfFileMerger()
    
    output_temp_documents_created = []
    
    for i in range(range_to):
    
        if i % interval_to == 0:
            temp_filename = "tempdocument"+str(len(output_temp_documents_created))+".pdf"
            merger.write(temp_filename)
            output_temp_documents_created.append(temp_filename)
            
            merger = PdfFileMerger()
            
        print "---------> "+str(i)
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                    
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
      
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
        
        for j in range(30):
            string_to_pdf(the_canvas,"---------> "+str(i) + title_string)
               
        the_canvas.save()
        
        input1 = PdfFileReader(tmpfile)
        
        merger.append(input1)
    
    final_output = PdfFileMerger()
    
    for filename in output_temp_documents_created:
                                       
        final_output.append(PdfFileReader(file(filename, 'rb')))
    
    
    final_output.write("tempdocument-final.pdf")

    

def string_to_pdf(canvas,string):

    splited_string = string.split("\n")
                            
    times = 0
    
    for item in splited_string:
        
        canvas.setFont("Helvetica", 11)
        canvas.drawString(2,800-(14*times),item)
        
        times +=1