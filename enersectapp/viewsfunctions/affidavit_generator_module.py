
import enersectapp

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection
from django import db

from enersectapp.models import *

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
import pytz
from tzlocal import get_localzone

from django.db.models import Count

import json 


import gc
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


import os
import shutil

import string
import random

Month_Dictionary = {"01":"January","1":"January","02":"February","2":"February","03":"March","3":"March","04":"April","4":"April","05":"May","5":"May","06":"June","6":"June","07":"July","7":"July","08":"August","8":"August","09":"September","9":"September","10":"October","11":"November","12":"December"}
max_characters_line = 95

def affidavit_generator(request):
    
    the_user = request.user
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    if len(the_user.groups.filter(name="TeamLeaders")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
        
    else:
    
        user_type = "user"

        
    if user_type != "superuser" and user_type != "TeamLeader" and user_type != "Client":
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        

    report_type = "affidavit"
    
    document_corpus_list = []
    
    watermark_name = ""

    
    try:
        affidavit_result = affidavit_mode(request)
        watermark_name = affidavit_result['watermark_name']
        
        if affidavit_result['response']:
        
            return affidavit_result['response']
        
        
    except:
    
        watermark_name = ""
        print "Failed to enter affidavit_mode"
      
    try:

        document_corpus_list = document_corpus_maker()
     
    except:
    
        document_corpus_list = []
         
    context = {'user_type':user_type,'the_user':the_user,
                'document_corpus_list':document_corpus_list,'watermark_name':watermark_name}
    
    return render(request,'enersectapp/affidavit_generator.html',context)


def document_corpus_maker():
    
    corpus_list = ["ICR","SRC","GRLV","ALBK","TRN"]
    
    all_documents = []
    
    for corpus_type in corpus_list:
    
        temp_documents = os.listdir('legaldiscoverytemp/output_files/'+corpus_type+"/")
        all_documents.extend(temp_documents)
    
    all_documents = sorted(all_documents)
    
    #print all_documents
    
    document_corpus_list = []
    
    icr_corpus_dict = {}
    icr_corpus_contents_list = []
    sourcepdfs_corpus_dict = {}
    sourcepdfs_corpus_contents_list = []
    grandelivre_corpus_dict = {}
    grandelivre_corpus_contents_list = []
    albaraka_corpus_dict = {}
    albaraka_corpus_contents_list = []
    transactions_corpus_dict = {}
    transactions_corpus_contents_list = []
    
    for file in all_documents:
        
        file_dict = {}
        
        if "ICR" in file:
            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            icr_corpus_contents_list.append(file_dict)
            
        if "SRC" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            sourcepdfs_corpus_contents_list.append(file_dict)
            
        if "GRLV" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            grandelivre_corpus_contents_list.append(file_dict)
            
        if "ALBK" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            albaraka_corpus_contents_list.append(file_dict)
            
        if "TRN" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            transactions_corpus_contents_list.append(file_dict)
            
            
            
    icr_corpus_dict["corpus_name"] = "ICR"
    icr_corpus_dict["corpus_contents"] = icr_corpus_contents_list
    
    sourcepdfs_corpus_dict["corpus_name"] = "SRC"
    sourcepdfs_corpus_dict["corpus_contents"] = sourcepdfs_corpus_contents_list
    
    grandelivre_corpus_dict["corpus_name"] = "GRLV"
    grandelivre_corpus_dict["corpus_contents"] = grandelivre_corpus_contents_list
    
    albaraka_corpus_dict["corpus_name"] = "ALBK"
    albaraka_corpus_dict["corpus_contents"] = albaraka_corpus_contents_list
    
    transactions_corpus_dict["corpus_name"] = "TRN"
    transactions_corpus_dict["corpus_contents"] = transactions_corpus_contents_list
    
    document_corpus_list.append(icr_corpus_dict)
    document_corpus_list.append(sourcepdfs_corpus_dict)
    document_corpus_list.append(grandelivre_corpus_dict)
    document_corpus_list.append(albaraka_corpus_dict)
    document_corpus_list.append(transactions_corpus_dict)
    
    
    return document_corpus_list 
    
def string_to_pdf(canvas,string):

    splited_string = string.split("\n")
                            
    times = 0
    
    for item in splited_string:
        
        canvas.setFont("Helvetica", 11)
        canvas.drawString(2,800-(14*times),item)
        
        times +=1
                            
def remove_template(template_object):

    print template_object
    
    try:
    
        with transaction.commit_on_success():
            for sourcedoc_template in template_object.sourcedoctypes_list.all():

                for extractionfield_template in sourcedoc_template.extraction_fields.all():
         
                    extractionfield_template.delete()
            
                sourcedoc_template.delete()

        template_object.delete()
        
        return True
        
    except:
    
        return False
        
   


def affidavit_mode(request):

    
    #If an AffidavitInstance already exists, take its' watermark_name,
    #if not, create an AffidavitInstance, which will have the default name "00000000"

    response = ""
    
    try:
    
        watermark_name = AffidavitInstance.objects.all()[0].watermark_name
        
    except:

        new_AffidavitInstance = AffidavitInstance()
        new_AffidavitInstance.save()
        
        watermark_name = ""
    
    
    try:
        
        affidavit_mode_action = request.POST["affidavit_action_mark"]


    except:

        affidavit_mode_action = ""

    
    print affidavit_mode_action
    
    if affidavit_mode_action == "create_instance_watermark":
        
            watermark_name = create_instance_watermark(request,watermark_name)
            print watermark_name
    
    if watermark_name != "":
    
        print "Watermark Generated, Instance Available"

        if affidavit_mode_action == "generate_corpus_files_action":
            
            generate_corpus_output(request,watermark_name)
    
        if affidavit_mode_action == "merge_corpus_files_action":
            
            response = merge_corpus_output(request,watermark_name)
    
        if affidavit_mode_action == "download_file_action":
            
            response = download_file_output(request,watermark_name)
    

    else:
    
        #The user hasn't generated a watermarked instance yet, so there is no possibility of creating any files
        #Return no values
    
        print "Default Affidavit Instance, no watermark generated"
    
    print "THIS IS WATERMARK --->" + watermark_name
    
    return {"watermark_name":watermark_name,"response":response}
    
    ## Loop to have a list of all files in the folder, and delete all the .pdfs
    
    ##~~~~delete_temp_affidavit_files()
    
    
    
    ##This block is functional, and merging all the things into one .PDF to be exported in the response
    #Changed to a .zip
    
    '''final_output = PdfFileMerger()
    
    partial_output = PdfFileMerger()
    
    outputStream = StringIO()

    print "-SHOULD HAPPEN JUST ONCE" 
    #final_output.append(PdfFileReader(temp_outputStream))
    
    for filename in output_temp_documents_created:
        print "---->"+str(filename)   
        #final_output.append(PdfFileReader(temp_output_item))
        partial_output.append(PdfFileReader(file(filename, 'rb')))
   
    #To isolate the generated report for the ICR corpus
   
    partial_filename = "legaldiscoverytemp/output_files/icr-affidavitofrecords-final.pdf"
    
    partial_output.write(partial_filename)
    
    ##
    
    final_output.append(PdfFileReader(file(partial_filename, 'rb')))
    
    final_output.write(outputStream)'''
    

    ## Loop to have a list of all files in the folder, '''and delete all the .pdfs'''
    
    '''file_list = os.listdir('legaldiscoverytemp/output_files/')'''#os.chdir('legaldiscoverytemp/output_files')
    
    '''for item in file_list:
    
        if ".pdf" in str(item):
            os.remove('legaldiscoverytemp/output_files/'+str(item))'''


def generate_corpus_output(request,watermark_name):
    
    try:
        corpus_to_include = request.POST["selected_corpus_mark"]
    except:
        corpus_to_include = ""
    
    documents_corpus_to_include_in_output = []
    documents_corpus_to_include_in_output.append(corpus_to_include)
    
    print corpus_to_include
    print documents_corpus_to_include_in_output
    
    if "ICR" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("ICR","cover")
        delete_temp_affidavit_files("ICR","partial")
        delete_temp_affidavit_files("ICR","merge")
        
        generate_icr_output(request,watermark_name)
        
    
    if "SRC" in documents_corpus_to_include_in_output:
        
        try:
            complete_corpus_mark = request.POST['complete_corpus_mark']
        except:
            complete_corpus_mark = ""
        
        if complete_corpus_mark != "complete":
        
            delete_temp_affidavit_files("SRC","cover")
            delete_temp_affidavit_files("SRC","partial")
            delete_temp_affidavit_files("SRC","merge")
        
        generate_sourcepdfs_output(request,watermark_name)
    
    if "GRLV" in documents_corpus_to_include_in_output:

        delete_temp_affidavit_files("GRLV","cover")
        delete_temp_affidavit_files("GRLV","partial")
        delete_temp_affidavit_files("GRLV","merge")

        generate_grandelivre_output(request,watermark_name)

    if "ALBK" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("ALBK","cover")
        delete_temp_affidavit_files("ALBK","partial")
        delete_temp_affidavit_files("ALBK","merge")
        
        generate_albaraka_output(request,watermark_name)
        
    if "TRN" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("TRN","cover")
        delete_temp_affidavit_files("TRN","partial")
        delete_temp_affidavit_files("TRN","merge")
        
        generate_transactions_output(request,watermark_name)


def generate_icr_output(request,watermark_name):

    try:
        max_documents = request.POST['select_max_documents']
    except:
        max_documents = "100"
        
    try:
        docs_per_pdf = request.POST['select_docs_per_pdf']
    except:
        docs_per_pdf = "25"

        
    if max_documents == "":
    
        max_documents = "100"
        
    if docs_per_pdf == "":
    
        docs_per_pdf = "25"
        
    max_documents = int(max_documents)
    docs_per_pdf = int(docs_per_pdf)
    
    max_characters_line = 95
    
    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []


    title_string = "Icr Corpus Report\n\n"

    local_tz = get_localzone()
    
    title_date = str(datetime.datetime.now().replace(tzinfo=local_tz).strftime("%d-%m-%Y %H:%M:%S %Z%z"))

    date_string = "   -This Corpus of Documents was generated on Date: "+title_date
    
    space_between = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    
    affidavit_instance = AffidavitInstance.objects.all()[0]
    affidavit_watermark = str(affidavit_instance.watermark_name)
    affidavit_date = str(affidavit_instance.modification_date.strftime("%d-%m-%Y %H:%M:%S %Z%z"))
    
    
    
    affidavit_string = "Contents Instance goes by the watermark name "+affidavit_watermark+",\nand was frozen on Date:"+affidavit_date
    
    cover_content = title_string + date_string + space_between + affidavit_string
    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,cover_content)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"ICR"+"/"+"ICR__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = PdfRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    page_count = 1
    pdf_string = ""
    
    #all_sourcedoctypes = SourceDocType.objects.filter(extraction_fields__isnull = False).distinct()

                                
    '''Iteration of all the DocTypes to select the appropriate documents (OcrEntries)'''

    '''with transaction.commit_on_success():
        for doctype in all_sourcedoctypes:
       
            #Takes the ones that fit with the doctype we are searching for

            corpus_pdfs_to_export = PdfRecord.objects.filter(audit_mark = "None").distinct()

            corpus_base = corpus_pdfs_to_export.filter(modified_document_type = doctype)

            corpus_final = corpus_base.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

            corpus_common_final = corpus_common_final | corpus_final
            

    corpus_common_final = corpus_common_final.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

    corpus_common_final = corpus_common_final[:max_documents]'''

    corpus_common_final = PdfRecord.objects.filter(affidavit_watermark_string = watermark_name).order_by('affidavit_uid_string')[:max_documents]

    did_page_jump = True
    
    with transaction.commit_on_success():
    
        for selected_entry_item in corpus_common_final:
    
            
            if doc_iterator % docs_per_pdf == 0 and doc_iterator != 0:
                

                if did_page_jump == False:

                    
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"ICR"+"/"+"ICR__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                did_page_jump = True
                
                db.reset_queries()
                
                pdf_string = ""

            if did_page_jump == True:
                      

                    pdf_string = ""
                    pdf_string += "                                                                                                                                 "+"ICR__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                    pdf_string +="\n\n\n"
                    page_count +=1    
                
            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["Month","Day","Year","Amount","Currency","Company","Piece_Number","Document_Number","Source_Bank_Account","PurchaseOrder_Number","Cheque_Number","Address","City","Country","Telephone","Page_Number","Notes","Translation_Notes"]
            corpus_sorting_fields = ["Month","Day","Year","Amount","Currency","IssueDate","Company","Piece_Number","Document_Number","Source_Bank_Account","PurchaseOrder_Number","Cheque_Number","Address","City","Country","Telephone","Page_Number","Notes","Translation_Notes"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = PdfRecord.objects.filter(pk = selected_entry_item.pk)

            for record in corpus_final:
                
                
                pdf_string += add_icr_entry_content(exhibit_count,record)
                
                pdf_string += '\n'
                pdf_string += '\n'
                
                did_page_jump = False
                
                if pdf_string.count('\n') > 44:
                

                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    
                    '''pdf_string = ""
                    pdf_string += "                                                                                                                                 "+"ICR__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                    pdf_string += '\n'
                    page_count +=1'''
                    
                    did_page_jump = True
                
                
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
      
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
        string_to_pdf(the_canvas,pdf_string)
               
        the_canvas.save()
        
        input1 = PdfFileReader(tmpfile)
        
        output.append(input1)
       
        
        '''Write command to finish and save new page'''
    

    try:

        temp_filename = "legaldiscoverytemp/output_files/"+"ICR"+"/"+"ICR__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"
            
            

def generate_sourcepdfs_output(request,watermark_name):

    try:
        max_documents = request.POST['select_max_documents']
    except:
        max_documents = "100"
        
    try:
        docs_per_pdf = request.POST['select_docs_per_pdf']
    except:
        docs_per_pdf = "500"

        
    if max_documents == "":
    
        max_documents = "100"
        
    if docs_per_pdf == "":
    
        docs_per_pdf = "500"
        
    max_documents = int(max_documents)
    docs_per_pdf = int(docs_per_pdf)
    
    max_characters_line = 95
    
    try:
        complete_corpus_mark = request.POST['complete_corpus_mark']
    except:
        complete_corpus_mark = ""
    
    #Initialize the Pdf to be written
 
    
    output = PdfFileMerger()
    
    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []
    


    if complete_corpus_mark != "complete":
    
        title_string = "Source Pdfs Corpus Report\n\n"

        local_tz = get_localzone()
        
        title_date = str(datetime.datetime.now().replace(tzinfo=local_tz).strftime("%d-%m-%Y %H:%M:%S %Z%z"))

        date_string = "   -This Corpus of Documents was generated on Date: "+title_date
        
        space_between = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        
        affidavit_instance = AffidavitInstance.objects.all()[0]
        affidavit_watermark = str(affidavit_instance.watermark_name)
        affidavit_date = str(affidavit_instance.modification_date.strftime("%d-%m-%Y %H:%M:%S %Z%z"))
        
        affidavit_string = "Contents Instance goes by the watermark name "+affidavit_watermark+",\nand was frozen on Date:"+affidavit_date
        
        cover_content = title_string + date_string + space_between + affidavit_string
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)

        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
  
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

        string_to_pdf(the_canvas,cover_content)
       
        the_canvas.save()
                        
        input1 = PdfFileReader(tmpfile)
         
        output.append(input1)
        
        exhibit_count = 1
        corpus_doccount = 1
        
        temp_filename = "legaldiscoverytemp/output_files/"+"SRC"+"/"+"SRC__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

        output.write(temp_filename)

        output_temp_documents_created.append(temp_filename)
    
    
    output = PdfFileMerger()
    
    
    corpus_common_final = PdfRecord.objects.none()
    
    starting_document = 0
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    page_count = 1
    pdf_string = ""
    
    all_sourcedoctypes = SourceDocType.objects.filter(extraction_fields__isnull = False).distinct()
    
                                
    '''Iteration of all the DocTypes to select the appropriate documents (OcrEntries)'''
    
    '''with transaction.commit_on_success():
        for doctype in all_sourcedoctypes:
       
            #Takes the ones that fit with the doctype we are searching for
            
            corpus_pdfs_to_export = PdfRecord.objects.filter(audit_mark = "None").distinct()
            
            corpus_base = corpus_pdfs_to_export.filter(modified_document_type = doctype)

            corpus_final = corpus_base.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

            corpus_common_final = corpus_common_final | corpus_final
            

    corpus_common_final = corpus_common_final.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')
    
    corpus_common_final = corpus_common_final[:max_documents]'''
  
    
    
    if complete_corpus_mark == "complete":
    
        max_documents = 10000000000000000
        docs_per_pdf = 500
        
        #500 is the only possible partition size
 
        corpus_type = "SRC"

        temp_list = os.listdir('legaldiscoverytemp/output_files/'+corpus_type+"/")
      
        if len(temp_list) > 0:
     
            filename = str(temp_list[len(temp_list)-1]).replace(corpus_type+"__"+str(watermark_name)+"__partial__","").replace(".pdf","")
            
            doc_partial_number = int(filename)
            
            
            #If there is more than 1 partial created, start iterating from the previous partial, instead of the last one
            
            if doc_partial_number > 1:
                
                doc_partial_number -= 1
                
            
            starting_document = (doc_partial_number * 500) - 500    
            
            exhibit_count = starting_document + 1
            corpus_doccount = doc_partial_number
            doc_iterator = starting_document - 1
            page_count = starting_document + 1
            
            
        

    corpus_common_final = PdfRecord.objects.filter(affidavit_watermark_string = watermark_name).order_by('affidavit_uid_string')[starting_document:max_documents]
    
    did_page_jump = False  

    
    print "------------- STARTING SOURCE PDFS ----------------"
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
        
            created_page = False
        
            
            if doc_iterator % docs_per_pdf == 0 and doc_iterator != 0:
            
                
                print "<-------------------------- "+str(doc_iterator)+" ---------------------->"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"SRC"+"/"+"SRC__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page == True
                
                db.reset_queries()

            
            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
            

            #Exhibit Title Pages + Pdfs Loop
            
            '''Write command to begin outputing to a new page'''
            
            doctype_name = selected_entry_item.sourcedoc_link.modified_document_type.pretty_name
            job_directory = selected_entry_item.sourcedoc_link.job_directory
            filename = selected_entry_item.sourcedoc_link.filename
 
            #pdf_string = "Exhibit "+str(exhibit_count)
            pdf_string = ""
            
            record_uid = selected_entry_item.sourcedoc_link.affidavit_uid_string

            pdf_string = ""
            pdf_string += "                                                                                                                    "+"SRC__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
            pdf_string +="\n\n\n"
            page_count +=1
             

            record = selected_entry_item
       
            pdf_string += add_sourcepdfs_entry_content(exhibit_count,record)
         
            '''pdf_string += "Exhibit #"+str(exhibit_count)+" , UID: "+str(record_uid)+", "+str(doctype_name)+":"
            pdf_string += "\n"
            pdf_string += "\n"
            
                        
            pdf_string += ".  - File Name is: "+str(filename)+", on Directory: "+str(job_directory)'''
            
            
            '''Write command to finish and save new page'''
            
            
            tmpfile = tempfile.SpooledTemporaryFile(1048576)
            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
            tmpfile.rollover()
            
            the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
            string_to_pdf(the_canvas,pdf_string)
               
            the_canvas.save()
                
            input1 = PdfFileReader(tmpfile)
        
            output.append(input1)
            

            '''Write command to begin outputing to a new page'''
            
            
            
            #source_url = "http://54.200.180.182/sourcepdfs/%s/%s" %(job_directory, filename)
                

            '''remoteFile = urlopen(Request(source_url)).read()
            memoryFile = StringIO(remoteFile)
            input_pdf = PdfFileReader(memoryFile)
            output.append(input_pdf)
            '''
            
            if "/srv/" in os.path.dirname(__file__):
                
                file_url = "%s/%s" %(job_directory, filename)
                
                source_url = os.path.join(os.path.abspath(enersectapp.__path__[0]),os.pardir,os.pardir,"/var/www/evs",file_url)
                
            else :
                #print str(os.path.abspath(enersectapp.__path__[0]))
                file_url = "%s/%s" %(job_directory, filename)
                
                source_url = os.path.join(os.path.abspath(enersectapp.__path__[0]), os.pardir ,"legaldiscoverytemp/source_pdfs",file_url)
                

            #tempfile_output = PdfFileMerger()
            
           
            output.append(PdfFileReader(file(source_url, 'rb')))
            
            #Problem in record PDF 144099 , job4 , scan1~2013_06_12_11_36_12_36.pdf
            '''Write command to finish and save new page'''
            
            db.reset_queries()

            exhibit_count += 1
            doc_iterator = exhibit_count - 1
 


   
    try:
    
        temp_filename = "legaldiscoverytemp/output_files/"+"SRC"+"/"+"SRC__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"
    

def generate_grandelivre_output(request,watermark_name):
    
    
    try:
        max_documents = request.POST['select_max_documents']
    except:
        max_documents = "100"
        
    try:
        docs_per_pdf = request.POST['select_docs_per_pdf']
    except:
        docs_per_pdf = "25"

        
    if max_documents == "":
    
        max_documents = "100"
        
    if docs_per_pdf == "":
    
        docs_per_pdf = "25"
        
    max_documents = int(max_documents)
    docs_per_pdf = int(docs_per_pdf)

    max_characters_line = 95
        
    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []


    title_string = "GrandeLivre Corpus Report\n\n"

    local_tz = get_localzone()
    
    title_date = str(datetime.datetime.now().replace(tzinfo=local_tz).strftime("%d-%m-%Y %H:%M:%S %Z%z"))

    date_string = "   -This Corpus of Documents was generated on Date: "+title_date
    
    space_between = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    
    affidavit_instance = AffidavitInstance.objects.all()[0]
    affidavit_watermark = str(affidavit_instance.watermark_name)
    affidavit_date = str(affidavit_instance.modification_date.strftime("%d-%m-%Y %H:%M:%S %Z%z"))
    
    affidavit_string = "Contents Instance goes by the watermark name "+affidavit_watermark+",\nand was frozen on Date:"+affidavit_date
    
    cover_content = title_string + date_string + space_between + affidavit_string
    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,cover_content)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    
    
    temp_filename = "legaldiscoverytemp/output_files/"+"GRLV"+"/"+"GRLV__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = PdfRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    page_count = 1
    pdf_string = ""

               
    corpus_common_final = InternalRecord.objects.filter(affidavit_watermark_string = watermark_name).order_by('affidavit_uid_string')[:max_documents]
    #corpus_common_final = InternalRecord.objects.all().order_by('Year','Month','Day')

    #corpus_common_final = corpus_common_final[:max_documents]

    
    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        
            if doc_iterator % docs_per_pdf == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                
                
                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"GRLV"+"/"+"GRLV__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            if (doc_iterator % docs_per_pdf == 0 or doc_iterator == 0) and did_page_jump == False:
       
                pdf_string = ""
                pdf_string += "                                                                                                                    "+"GRLV__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                pdf_string +="\n\n\n"
                page_count +=1    
                
            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["IssueDate","Credit","Piece_Number","Day","Month","Year","NoPiece","ExchangeRate","Company","AccountNum","NoMvt","Memo","Lett","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["IssueDate","Credit","Piece_Number","Day","Month","Year","NoPiece","ExchangeRate","Company","AccountNum","NoMvt","Memo","Lett","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = InternalRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                pdf_string += add_grandelivre_entry_content(exhibit_count,record)
      
                '''Write command to output the existing pdf_string variable as a new row, then line break'''
                
                pdf_string += '\n'
                pdf_string += '\n'
                
                did_page_jump = False
                
                if pdf_string.count('\n') > 44:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                    pdf_string += "                                                                                                                    "+"GRLV__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                    pdf_string +="\n\n\n"
                    page_count +=1

                    did_page_jump = True
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
      
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
        string_to_pdf(the_canvas,pdf_string)
               
        the_canvas.save()
        
        input1 = PdfFileReader(tmpfile)
        
        output.append(input1)
       
        
        '''Write command to finish and save new page'''
    

    try:

        temp_filename = "legaldiscoverytemp/output_files/"+"GRLV"+"/"+"GRLV__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"


def generate_albaraka_output(request,watermark_name):
    
    
    try:
        max_documents = request.POST['select_max_documents']
    except:
        max_documents = "100"
        
    try:
        docs_per_pdf = request.POST['select_docs_per_pdf']
    except:
        docs_per_pdf = "25"

        
    if max_documents == "":
    
        max_documents = "100"
        
    if docs_per_pdf == "":
    
        docs_per_pdf = "25"
        
    max_documents = int(max_documents)
    docs_per_pdf = int(docs_per_pdf)
   

    max_characters_line = 95
   
    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []

    title_string = "AlBaraka Corpus Report\n\n"

    local_tz = get_localzone()
    
    title_date = str(datetime.datetime.now().replace(tzinfo=local_tz).strftime("%d-%m-%Y %H:%M:%S %Z%z"))

    date_string = "   -This Corpus of Documents was generated on Date: "+title_date
    
    space_between = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    
    affidavit_instance = AffidavitInstance.objects.all()[0]
    affidavit_watermark = str(affidavit_instance.watermark_name)
    affidavit_date = str(affidavit_instance.modification_date.strftime("%d-%m-%Y %H:%M:%S %Z%z"))
    
    affidavit_string = "Contents Instance goes by the watermark name "+affidavit_watermark+",\nand was frozen on Date:"+affidavit_date
    
    cover_content = title_string + date_string + space_between + affidavit_string
    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,cover_content)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"ALBK"+"/"+"ALBK__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = BankRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    page_count = 1
    pdf_string = ""

               
    corpus_common_final = BankRecord.objects.filter(affidavit_watermark_string = watermark_name).order_by('affidavit_uid_string')[:max_documents]
    #corpus_common_final = BankRecord.objects.all().order_by('ValueYear','ValueMonth','ValueDay')

    #corpus_common_final = corpus_common_final[:max_documents]

    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        
            if doc_iterator % docs_per_pdf == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                print "---------"+str("ALBK")+"--------"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"ALBK"+"/"+"ALBK__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                
            if (doc_iterator % docs_per_pdf == 0 or doc_iterator == 0) and did_page_jump == False:
    
    
                pdf_string = ""
                pdf_string += "                                                                                                                      "+"ALBK__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                pdf_string +="\n\n\n"
                page_count +=1

                
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["Amount","PostDay","PostMonth","PostYear","ValueDay","ValueMonth","ValueYear","Libelle","Reference","Description","TransactionId","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["Amount","PostDay","PostMonth","PostYear","ValueDay","ValueMonth","ValueYear","Libelle","Reference","Description","TransactionId","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = BankRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                

                pdf_string += add_albaraka_entry_content(exhibit_count,record)

                pdf_string += '\n'
                pdf_string += '\n'
                
                did_page_jump = False
                
                if pdf_string.count('\n') > 44:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""

                    pdf_string += "                                                                                                                      "+"ALBK__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                    pdf_string +="\n\n\n"
                    page_count +=1

                    did_page_jump = True
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
      
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
        string_to_pdf(the_canvas,pdf_string)
               
        the_canvas.save()
        
        input1 = PdfFileReader(tmpfile)
        
        output.append(input1)
       
        
        '''Write command to finish and save new page'''
    

    try:

        temp_filename = "legaldiscoverytemp/output_files/"+"ALBK"+"/"+"ALBK__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"


def generate_transactions_output(request,watermark_name):
    
    
    try:
        max_documents = request.POST['select_max_documents']
    except:
        max_documents = "100"
        
    try:
        docs_per_pdf = request.POST['select_docs_per_pdf']
    except:
        docs_per_pdf = "25"

        
    if max_documents == "":
    
        max_documents = "100"
        
    if docs_per_pdf == "":
    
        docs_per_pdf = "25"
        
    max_documents = int(max_documents)
    docs_per_pdf = int(docs_per_pdf)
    
    max_characters_line = 95
    
    #max_documents = 1000000

    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []

    title_string = "Transactions Corpus Report\n\n"

    local_tz = get_localzone()
    
    title_date = str(datetime.datetime.now().replace(tzinfo=local_tz).strftime("%d-%m-%Y %H:%M:%S %Z%z"))

    date_string = "   -This Corpus of Documents was generated on Date: "+title_date
    
    space_between = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    
    affidavit_instance = AffidavitInstance.objects.all()[0]
    affidavit_watermark = str(affidavit_instance.watermark_name)
    affidavit_date = str(affidavit_instance.modification_date.strftime("%d-%m-%Y %H:%M:%S %Z%z"))
    
    affidavit_string = "Contents Instance goes by the watermark name "+affidavit_watermark+",\nand was frozen on Date:"+affidavit_date
    
    cover_content = title_string + date_string + space_between + affidavit_string
    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,cover_content)
           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"TRN"+"/"+"TRN__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = BankRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    page_count = 1
    pdf_string = ""

               
    corpus_common_final = TransactionTable.objects.filter(affidavit_watermark_string = watermark_name).order_by('affidavit_uid_string')[:max_documents]
    #corpus_common_final = TransactionTable.objects.all().order_by('ValueYear','ValueMonth','ValueDay')

    #corpus_common_final = corpus_common_final[:max_documents]

    
    
    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        

            if doc_iterator % docs_per_pdf == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    #pdf_string = ""
                
                

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                print "---------"+str("TRN")+"--------"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"TRN"+"/"+"TRN__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        
            if (doc_iterator % docs_per_pdf == 0 or doc_iterator == 0) and did_page_jump == False:
            
                pdf_string += "                                                                                                                  "+"TRN__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                pdf_string +="\n\n\n"
                page_count +=1
                
            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["NumberBankRecordIndexes","BankRecordsUIDArray","NumberInternalRecordIndexes","InternalRecordUIDArray","CompletePostDate","CompleteValueDate","DateDiscrepancy","Amount","AmountDiscrepancy","ValueYear","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["NumberBankRecordIndexes","BankRecordsUIDArray","NumberInternalRecordIndexes","InternalRecordUIDArray","CompletePostDate","CompleteValueDate","DateDiscrepancy","Amount","AmountDiscrepancy","ValueYear","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = TransactionTable.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                record_uid = record.affidavit_uid_string
                
                pdf_content = add_transactions_entry_content(exhibit_count,record)
                
                if len(pdf_content) > 0:
                    pdf_string += pdf_content
                    
                    pdf_string += add_transactions_entry_content_internal(record)

                    pdf_string += add_transactions_entry_content_albaraka(record)
       
                    pdf_string += "\n\n     -Transaction Reference UID: ["+record_uid+"]"

                pdf_string += '\n'
                pdf_string += '\n'
                
                '''pdf_string += "Exhibit #"+str(exhibit_count)+" , UID: "+str(record_uid)+":"
                pdf_string += "\n"
                pdf_string += "\n"
                
                show_date = str(record.ValueDay)+"/"+str(record.ValueMonth)+"/"+str(record.ValueYear)
                if show_date == "XX/XX/XXXX" or show_date == "":
                    show_date = "(No Date)"
                show_amount = record.Amount    
                if show_amount == "":
                    show_amount = "(No Amount)"
                show_currency = record.BankCurrency    
                if show_currency == "":
                    show_currency = "(No Currency)"
                
                pdf_string += ".  -This Document is on Date: "+str(show_date)+" and refers to Amount: "+str(show_amount)+" "+str(show_currency)
                pdf_string += "\n"
                pdf_string += "\n"
                pdf_string += ".              -"
                
                
                for field_name in corpus_include_fields:
                    
                    try:
                        field_content = str(getattr(record, field_name))
                    except:
                        field_content = ""
                    
                    
                    try:
                        
                        try:
                            
                            if field_name == "BankRecordsUIDArray" or field_name == "InternalRecordUIDArray":
                            
                                if field_name == "BankRecordsUIDArray":
                                    corpus_tempname = "ALBK"
                                else:
                                    corpus_tempname = "GRLV"
                            
                                test_string = "\n"
                                test_string2 = ".              -"
                                test_string3 = ".                   -"
                                test_string4 = test_string + test_string3
                                
                                records_list = field_content.split(",")

                                field_content = ""
                                
                                records_count = 0
                                
                                line_break_count = 1
                                
                                temp_sum_line = 0
                                
                                for actual_record in records_list:
                                
                                    if actual_record != "":
                                        item_content = actual_record
                                        actual_record = actual_record.replace(item_content,corpus_tempname+"__"+str(watermark_name)+"__element__"+item_content)
                                        
                                    if records_count == 0:
                                        actual_record = "["+actual_record
                                    if records_count == len(records_list)-1:
                                        actual_record = actual_record + "]"
                                
                                    temp_sum_line = len(field_content) + len(actual_record)
                                
                                    #If length of string plus new content is greater than the line width with margin, introduce
                                    #a new indented line
                                
                                    if temp_sum_line >= 60 * line_break_count:
                                    
                                        field_content += test_string4
                                        line_break_count += 1
                                    
                                    field_content += str(actual_record)+","
                                    
                                    records_count += 1
                                    
                                
                                field_content += test_string + test_string2
                                
                            
                            elif (len(pdf_string.split("\n")[-1]) + len(" "+field_name+" "+field_content)) > max_characters_line:
                                test_string = "\n"
                                test_string2 = ".              -"
                                test_string4 = ""
                            else:
                                test_string = ""
                                test_string2 = ""
                                test_string4 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content !="None" and field_content !="XX/XX/XXXX" and field_content != "*":
                                
                                pdf_string += " "+test_string+test_string2+field_name+ test_string4 +" "+field_content
                                
                                if pdf_string.count('\n') >= 44:
                
                                    pdf_string_count = pdf_string.count('\n')
                
                                    #pdf_string += '\n'
                    
                                    pdf_string_templist = pdf_string.split('\n')
                                    pdf_string_temp = ""
                                    
                                    iterator_index = 0
                                    iterator_set = 0
                                    
                                    pdf_string = ""
                                    
                                    for list_element in pdf_string_templist:

                                        iterator_index += 1
                                        iterator_set += 1
                                        
                                        #Control so it will never start the output of an Exhibit at the end of a page.
                                        #Instead, it will skip it for the next page.
                                        
                                        if iterator_set == len(pdf_string_templist):
                                        
                                            if "Exhibit" in list_element:

                                                pdf_string = list_element
                                                
                                            else:    

                                                pdf_string = ".              -"
                                            
                                                 

                                        pdf_string_temp += list_element
                                        pdf_string_temp += '\n'
                                        
                                        #Include all the strings contained in the page
                                        
                                        did_page_jump = False
                                        
                                        if iterator_set == len(pdf_string_templist):
                                            
                                            #pdf_string = ".              -"
                                            
                                            iterator_set = 0
                                        
                                            tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                
                                            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                            tmpfile.rollover()
                                          
                                            the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                                            string_to_pdf(the_canvas,pdf_string_temp)
                                                   
                                            the_canvas.save()
                                            
                                            input1 = PdfFileReader(tmpfile)
                                            
                                            output.append(input1)
                                            
                                            pdf_string_temp = ""
                                            temp_str = pdf_string
                                            pdf_string =""
                                            pdf_string += "                                                                                                                  "+"TRN__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                                            pdf_string +="\n\n\n"
                                            pdf_string += temp_str
                                            page_count +=1

                                            did_page_jump = True
                                
                              
                        except:
                            test_string = ""
                        
                    except:
                        pdf_string += " "'''
                        
                
                '''Write command to output the existing pdf_string variable as a new row, then line break'''
                
                pdf_string += '\n'
                
                #Before adding Albarakas, limit of lines was > 45
                if pdf_string.count('\n') > 45:
                
                    temp_pdf_string = ""
                
                    if pdf_string.count('\n') > 60:
                    
                        temp_pdf_string = pdf_string.split('\n')[50:]
                        temp_pdf_string = '\n'.join(temp_pdf_string)
                        pdf_string = pdf_string.split('\n')[:50]
                        pdf_string = '\n'.join(pdf_string)
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                    
                    pdf_string += "                                                                                                                  "+"TRN__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                    pdf_string +="\n\n\n"
                    
                    if len(temp_pdf_string) > 0:
                        pdf_string += temp_pdf_string
                    
                    page_count +=1

                    did_page_jump = True
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
      
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
        string_to_pdf(the_canvas,pdf_string)
               
        the_canvas.save()
        
        input1 = PdfFileReader(tmpfile)
        
        output.append(input1)
       
        
        '''Write command to finish and save new page'''
    

    try:

        temp_filename = "legaldiscoverytemp/output_files/"+"TRN"+"/"+"TRN__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"        

def merge_corpus_output(request,watermark_name):

    try:
        corpus_to_include = request.POST["selected_corpus_mark"]
    except:
        corpus_to_include = ""

    corpus_to_include = str(corpus_to_include)



    file_list = os.listdir('legaldiscoverytemp/output_files/'+corpus_to_include+'/')

    file_list = sorted(file_list)

    final_output = PdfFileMerger()


    partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+str(corpus_to_include)+"__"+str(watermark_name)+"__cover__0000001.pdf"
    

    final_output.append(PdfFileReader(file(partial_filename, 'rb')))
    

    partial_output = PdfFileMerger()

    outputStream = StringIO()

    #Line added to include the cover in the .zip file
    partial_output.append(PdfFileReader(file(partial_filename, 'rb')))
    
    #final_output.append(PdfFileReader(temp_outputStream))
    
    count = 0
    
    for filename in file_list:
        print "---->"+str(filename)
                  
        #final_output.append(PdfFileReader(temp_output_item))
        if corpus_to_include in filename and "partial" in filename:
            print "---->"+str(corpus_to_include) 
            partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+filename
            partial_output.append(PdfFileReader(file(partial_filename, 'rb')))

            count += 1
   
    #To isolate the generated report for the selected corpus

    partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+corpus_to_include+"__"+str(watermark_name)+"__merge__"+str(count)+"_files.pdf"

    partial_output.write(partial_filename)

    ##
    
    final_output.append(PdfFileReader(file(partial_filename, 'rb')))

    final_output.write(outputStream)

    ##
    
    myZipFile = shutil.make_archive("legaldiscoverytemp/output_files_final/"+corpus_to_include+"/"+corpus_to_include+"__"+str(watermark_name)+"__merge__"+str(count+1)+"_files", "zip", "legaldiscoverytemp/output_files"+"/"+corpus_to_include)
    #myZipFile.write(outputStream)

    test_file = open("legaldiscoverytemp/output_files_final/"+corpus_to_include+"/"+corpus_to_include+"__"+str(watermark_name)+"__merge__"+str(count+1)+"_files.zip", "rb")

    ###
    
    ##If .pdf instead
    #response = HttpResponse(mimetype="application/pdf")
    #response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/output_files/legal_discovery_report_%s.pdf' %(title_date)

    response = HttpResponse(test_file, mimetype="application/zip")

    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))
    
    response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/output_files_final/'+corpus_to_include+'/'+corpus_to_include+'__'+str(watermark_name)+'__'+str(count+1)+'_files_report__%s.zip' %(title_date)

    ##If .pdf instead, this line is necessary:
    #response.write(outputStream.getvalue())
    return response
    
def download_file_output(request,watermark_name):

    try:
        corpus_to_include = request.POST["selected_corpus_mark"]
    except:
        corpus_to_include = ""

    corpus_to_include = str(corpus_to_include)

    try:
        file_to_include = request.POST["selected_file_mark"]
    except:
        file_to_include = ""

    file_to_include = str(file_to_include)
        

    final_output = PdfFileMerger()

    
    outputStream = StringIO()
    

    partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+str(file_to_include)
    

    final_output.append(PdfFileReader(file(partial_filename, 'rb')))
    

    final_output.write(outputStream)


    ###

    ##If .pdf instead
    response = HttpResponse(mimetype="application/pdf")

    response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/output_files/'+corpus_to_include+'/'+str(file_to_include)


    ##If .pdf instead, this line is necessary:
    response.write(outputStream.getvalue())

    return response
    
    
def create_instance_watermark(request,watermark_name):

    #Brings up a new watermark of 8 random digits in all caps

    try:
        new_watermark = id_generator()
        delete_temp_affidavit_files("all","all")

        AffidavitInstance.objects.all().delete()

        new_AffidavitInstance = AffidavitInstance()
        new_AffidavitInstance.watermark_name = new_watermark
        
        new_AffidavitInstance.save()
        
        affidavit_watermark_everything(new_watermark,new_AffidavitInstance)

        return new_watermark
    except:
        
        return False
    
def affidavit_watermark_everything(watermark_name,watermark_instance):

    corpus_icr = PdfRecord.objects.none()
    
    '''all_sourcedoctypes = SourceDocType.objects.filter(extraction_fields__isnull = False).distinct()
     
    #Iteration of all the DocTypes to select the appropriate documents (OcrEntries)

    with transaction.commit_on_success():
        for doctype in all_sourcedoctypes:
       
            #Takes the ones that fit with the doctype we are searching for

            corpus_icr_to_export = PdfRecord.objects.filter(audit_mark = "None").distinct()

            corpus_base = corpus_icr_to_export.filter(modified_document_type = doctype)

            corpus_final = corpus_base.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

            corpus_icr = corpus_icr | corpus_final'''
    
    
    blank = SourceDocType.objects.get(name = "blank")
    blank_probable = SourceDocType.objects.get(clean_name = "blank_probable")
    other = SourceDocType.objects.get(name = "other")
    misc = SourceDocType.objects.get(name = "misc")
    
    corpus_icr = PdfRecord.objects.filter(audit_mark = "None").exclude(EntryByCompany__name = "TestGroup").exclude(EntryAuthor__username = "nemot").exclude(sourcedoc_link__corrupt = "yes").order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day').exclude(modified_document_type__name = blank).exclude(modified_document_type__name = other).exclude(modified_document_type__name = blank_probable).exclude(modified_document_type__name = misc).distinct()
    
    #corpus_sourcepdfs will be represented in the corpus_icr loop, by the field sourcedoc_link
    #corpus_sourcepdfs = SourcePdf.objects.all().distinct()

    corpus_grandelivre = InternalRecord.objects.all().order_by('Year','Month','Day').distinct()

    corpus_albaraka = BankRecord.objects.all().order_by('ValueYear','ValueMonth','ValueDay').distinct()

    corpus_transactions = TransactionTable.objects.all().order_by('ValueYear','ValueMonth','ValueDay').distinct()

    with transaction.commit_on_success():
        
        db.reset_queries()
        
        corpus_tag = "ICR"
        corpus_tag2 = "SRC"
        corpus_doccount = 1
   
        for element in corpus_icr:
     
            actual_count = str(corpus_doccount).zfill(7) 
     
            element.affidavit_watermark_string = watermark_name
            #element.actual_affidavit_watermark = watermark_instance
            element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + actual_count
            
            element.save()
            
            element.sourcedoc_link.affidavit_watermark_string = watermark_name
            #element.sourcedoc_link.actual_affidavit_watermark = watermark_instance
            element.sourcedoc_link.affidavit_uid_string = corpus_tag2 + "__" + str(watermark_name) + "__element__" + actual_count
            
            element.sourcedoc_link.save()
            '''try:
                element.ocrrecord_link.Day = element.ocrrecord_link.Day.zfill(2)
                element.ocrrecord_link.Month = element.ocrrecord_link.Month.zfill(2)
            except:
                filler = 0
            element.ocrrecord_link.affidavit_watermark_string = watermark_name
            #element.sourcedoc_link.actual_affidavit_watermark = watermark_instance
            element.ocrrecord_link.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + actual_count
            
            element.ocrrecord_link.save()'''
    
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)

            
        
    with transaction.commit_on_success():
        
        db.reset_queries()
        
        corpus_tag = "GRLV"
        corpus_doccount = 1
    
    
        for element in corpus_grandelivre:
        
            element.affidavit_watermark_string = watermark_name
            #element.actual_affidavit_watermark = watermark_instance
            element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + str(corpus_doccount).zfill(7) 
            try:
                element.Day = element.Day.zfill(2)
                element.Month = element.Month.zfill(2)
            except:
                filler = 0
            element.save()
            
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)+"----> PK : "+str(element.pk)
            
              
    
    with transaction.commit_on_success():
    
        db.reset_queries()
        
        corpus_tag = "ALBK"   
        corpus_doccount = 1  
    
        for element in corpus_albaraka:
        
            element.affidavit_watermark_string = watermark_name
            #element.actual_affidavit_watermark = watermark_instance
            element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + str(corpus_doccount).zfill(7) 
            try:
                element.PostDay = element.PostDay.zfill(2)
                element.PostMonth = element.PostMonth.zfill(2)
                element.ValueDay = element.ValueDay.zfill(2)
                element.ValueMonth = element.ValueMonth.zfill(2)
            except:
                filler = 0
            
            element.save()
            
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)
        
        
    
    with transaction.commit_on_success():
    
        db.reset_queries()
        
        corpus_tag = "TRN"
        corpus_doccount = 1
    
        for element in corpus_transactions:
        
            if len(element.AffidavitString) > 0:
                element.affidavit_watermark_string = watermark_name
                #element.actual_affidavit_watermark = watermark_instance
                element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + str(corpus_doccount).zfill(7) 
        
                element.BankRecordsUIDArray = str(element.bank_records_list.all().values_list('affidavit_uid_string',flat=True)).replace("ALBK" + "__" + str(watermark_name) + "__element__","").replace("u","").replace("'","").replace("[","").replace("]","")
                
                element.InternalRecordUIDArray = str(element.internal_records_list.all().values_list('affidavit_uid_string',flat=True)).replace("GRLV" + "__" + str(watermark_name) + "__element__","").replace("u","").replace("'","").replace("[","").replace("]","")   
                try:
                    element.PostDay = element.PostDay.zfill(2)
                    element.PostMonth = element.PostMonth.zfill(2)
                    element.ValueDay = element.ValueDay.zfill(2)
                    element.ValueMonth = element.ValueMonth.zfill(2)
                except:
                    filler = 0
                    
                element.save()
                
                prepareAffidavitString(element,corpus_doccount)
            
                corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)
    


    
def delete_temp_affidavit_files(corpus,partial_or_merge):

    corpus_list = ["ICR","SRC","GRLV","ALBK","TRN"]

    file_list = []
    
    if corpus == "all":
    
        for corpus_type in corpus_list:
            print corpus_type
            temp_list = os.listdir('legaldiscoverytemp/output_files/'+corpus_type+"/")#os.chdir('legaldiscoverytemp/output_files')
            file_list.extend(temp_list)
    
    else:
    
        file_list = os.listdir('legaldiscoverytemp/output_files/'+corpus+"/")#os.chdir('legaldiscoverytemp/output_files')

        
    for item in file_list:
    
        to_remove = False
        
        if partial_or_merge == "all":
 
                to_remove = True

        if ".pdf" in str(item):

            if corpus in str(item):

                if partial_or_merge == "partial":
                
                    if "partial" in str(item):
                    
                        to_remove = True
                
                if partial_or_merge == "merge":    
                
                    if "merge" in str(item):
                    
                        to_remove = True
                
                if partial_or_merge == "cover":  
                
                    if "cover" in str(item):
                    
                        to_remove = True
          

            if to_remove == True:    
        
                if corpus == "all":
                    for corpus_type in corpus_list:
            
                        try:
                            os.remove('legaldiscoverytemp/output_files/'+corpus_type+'/'+str(item))    
                        except:
                            #print "Not in that folder"
                            
                            try:
                                os.remove('legaldiscoverytemp/output_files_final/'+corpus_type+'/'+str(item))    
                            except:
                                "Not in that folder"
                            

                else:

                    try:
                        os.remove('legaldiscoverytemp/output_files/'+corpus+'/'+str(item))    
                    except:
                        #print "Not in that folder"
                            
                        try:
                            os.remove('legaldiscoverytemp/output_files_final/'+corpus+'/'+str(item))    
                        except:
                            "Not in that folder"
                            
    
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
        

        
def test_length_add_line(previous_string, additional_string):


    return_string = ""

    if (len(previous_string.split("\n")[-1])) + len(additional_string) > max_characters_line:
    
        return_string = "\n    "
    
    return_string = str(previous_string) + str(return_string) + str(additional_string) 
    
    return return_string    

def test_icr_content(field_name,record):

    actual_content = ""

    if field_name == "IssueDate":
        try:
            
            field_content = str(record.ocrrecord_link.IssueDate)

            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "Blank" and field_content != "*" and field_content != "NaN":
     
                            
                if record.ocrrecord_link.Day != "NaN" and record.ocrrecord_link.Day != "" and record.ocrrecord_link.Day != "*":
                    day_string = str(record.ocrrecord_link.Day)
                else:
                    day_string = "an unknown Day"
                    
      
                if record.ocrrecord_link.Month != "NaN" and record.ocrrecord_link.Month != "" and record.ocrrecord_link.Month != "*":
                    
                    try:
                    
                        month_string = Month_Dictionary[str(record.ocrrecord_link.Month)]
                    
                    except:
                    
                        month_string = str(record.ocrrecord_link.Month)
                else:
                    month_string = "an unknown Month"
                    
         
                
                if record.ocrrecord_link.Year != "NaN" and record.ocrrecord_link.Year != "" and record.ocrrecord_link.Year != "*":
                    year_string = str(record.ocrrecord_link.Year)
                else:
                    year_string = "an unknown Year"

                actual_content = month_string + " " + day_string + ", " + year_string
            
            else:
                
                actual_content = "an unknown Date, "
        except:
        
            actual_content = "an unknown Date, "
    
    if field_name == "Document_Number":
        try:
            field_content = str(record.ocrrecord_link.Document_Number)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
    
    if field_name == "Piece_Number":
        try:
            field_content = str(record.ocrrecord_link.Piece_Number)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:

            actual_content = "unknown"
            
    if field_name == "Amount":
        try:
            field_content = str(record.ocrrecord_link.Amount)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "an unknown Amount"
        except:
        
            actual_content = "an unknown Amount"
            
    if field_name == "Currency":
        try:
            field_content = str(record.ocrrecord_link.Currency)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
         
        except:
        
            actual_content = "unknown"
         
    if field_name == "Company":
        try:
            field_content = str(record.ocrrecord_link.Company)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and field_content != "MISSING NAME" and field_content != "UNREADABLE NAME" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "an unknown Recipient"
        except:
        
            actual_content = "an unknown Recipient"
            
    if field_name == "Address":
        try:
            field_content = str(record.ocrrecord_link.Address)

            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
            
    if field_name == "Telephone":
        try:
            field_content = str(record.ocrrecord_link.Telephone)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
            
    if field_name == "Location":
        try:
            city_string = str(record.ocrrecord_link.City)
            country_string = str(record.ocrrecord_link.Country)
            
            field_content = city_string
            
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                city_string = field_content
                city = True
                
            else:
            
                city = False
                city_string = "an unknown City"
                
            field_content = country_string
            
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                country_string = ", in "+field_content
                country = True
                
            else:
            
                country = False
                country_string = ", in an unknown Country"   
        
            
            actual_content = city_string + country_string

            
            if city == False and country == False:
            
                actual_content = "an unknown Location"
        except:

            actual_content = "an unknown Location"
    
    #if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and "arabic translation" not in field_content and field_content != "no" and field_content != "Blank" and field_content != "*":
    
    if field_name == "sourcepdf_uid":
        try:
            field_content = str(record.sourcedoc_link.affidavit_uid_string)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "No_Linked_SourceDoc"
        except:
        
            actual_content = "No_Linked_SourceDoc"
    
    
    if field_name == "ExtraFields":
    
        try:
            sourcebankaccount_string = str(record.ocrrecord_link.Source_Bank_Account)
            purchaseorder_string = str(record.ocrrecord_link.PurchaseOrder_Number)
            chequenumber_string = str(record.ocrrecord_link.Cheque_Number)
            
            field_content = sourcebankaccount_string
            
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                sourcebankaccount_string = "Transference was made from Account " + field_content + ".\n"
                sourcebankaccount = True

            else:
            
                sourcebankaccount = False
                sourcebankaccount_string = ""
                
            field_content = purchaseorder_string
            
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                purchaseorder_string = "The Purchase Order number is "+ field_content + ".\n"
                purchaseorder = True

            else:
            
                purchaseorder = False
                purchaseorder_string = ""   
        
            field_content = chequenumber_string
            
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                chequenumber_string = "An additional Cheque Number was provided: "+field_content + ".\n"
                chequenumber = True

            else:
            
                chequenumber = False
                chequenumber_string = ""   
            

            if sourcebankaccount == True or purchaseorder == True or chequenumber == True:
         
                actual_content = "Extra information: \n      " + sourcebankaccount_string + purchaseorder_string + chequenumber_string
                
        except:

            actual_content = ""

    return actual_content
    
def add_icr_entry_content(exhibit_count, record):


    return_string = ""

    doctype_pretty_name = record.modified_document_type.pretty_name
           
    ocr_record_final = record.ocrrecord_link
    sourcedoc_final = record.sourcedoc_link

    record_uid = record.affidavit_uid_string
    sourcepdf_uid = sourcedoc_final.affidavit_uid_string

    pdf_string = ""
    
    '''Item 1. On April 17, 2006, Al Baraka Bank processed Payment Order FT224 transferring EUR

        7,100.00 (CDN $9,976.21) to Bachar El Ghussein. [BFG-1-SOURCE] These funds were recorded 

        in the 2006 accounting of NA Solid Petroserve Ltd.'s Tunisian Branch with journal entry 474 as 

        having been sent to Fluid Control Europe. [BFG-1-ACCT]'''
    #corpus_include_fields = ["Month","Day","Year","Amount","Currency","Company","Piece_Number","Document_Number","Source_Bank_Account","PurchaseOrder_Number","Cheque_Number","Address","City","Country","Telephone","Page_Number","Notes","Translation_Notes"]

    pdf_string += "Item #"+str(exhibit_count)+". "+str(doctype_pretty_name)+":"
    pdf_string += "\n"

    pdf_string += "    On "
    #On April 17, 2006, / On an unknown Date,
    pdf_string = test_length_add_line(pdf_string, test_icr_content("IssueDate",record))

    pdf_string += " "
    
    pdf_string = test_length_add_line(pdf_string, "a "+doctype_pretty_name+" document of number ")
    

    # X Document_Number / unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Document_Number",record))
    pdf_string = test_length_add_line(pdf_string, " and piece number ")
    
    
    
    # X Piece Number/ unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Piece_Number",record))
    pdf_string = test_length_add_line(pdf_string, " was processed, transferring ")

    

    # X Amount/ an unknown Amount
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Amount",record))
    pdf_string = test_length_add_line(pdf_string, " of Currency ")
    
    
    # X Currency/ unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Currency",record))
    pdf_string = test_length_add_line(pdf_string, " to ")
    
  
    # X Company / an unknown Recipient
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Company",record))
    pdf_string = test_length_add_line(pdf_string, ", with Address ")
    
    
    # X Address / unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Address",record))
    pdf_string = test_length_add_line(pdf_string, " and Phone Number ")
    
    
    # X Telephone / unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Telephone",record))
    pdf_string = test_length_add_line(pdf_string, " residing in ")
    
    
    # X City, Country / an unknown Location
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Location",record))
    pdf_string += ". "
    

    # Extra fields: Cheque Number, Purchase Order Number, Source Bank Account
    
    pdf_string = test_length_add_line(pdf_string, test_icr_content("ExtraFields",record))
    
    pdf_string += "\n\n     "
    
    # [sourcepdf_uid]

    pdf_string = test_length_add_line(pdf_string, "Associated SRC Document UID: ["+test_icr_content("sourcepdf_uid",record)+"]")
    
    pdf_string += "\n     "
    
    pdf_string = test_length_add_line(pdf_string, "ICR Item Reference UID: ["+str(record_uid)+"]")
    

    return_string = pdf_string

    return return_string

def test_sourcepdfs_content(field_name,record):

    actual_content = ""

    if field_name == "Filename":
        try:
            field_content = str(record.filename)
        
            actual_content = field_content

        except:
        
            actual_content = "unknown"
    
    if field_name == "JobDirectory":
        try:
            field_content = str(record.job_directory)
        
            actual_content = field_content

        except:
        
            actual_content = "unknown"
    
    if field_name == "JobDirectory":
        try:
            field_content = str(record.job_directory)
        
            actual_content = field_content

        except:
        
            actual_content = "unknown"
    
    
    if field_name == "icr_uid":
        try:
            field_content = str(record.affidavit_uid_string)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "No_Linked_Icr"
        except:
        
            actual_content = "No_Linked_Icr"
    
    return actual_content
    
def add_sourcepdfs_entry_content(exhibit_count, record):


    return_string = ""

    doctype_pretty_name = record.modified_document_type.pretty_name

    sourcedoc_final = record.sourcedoc_link

    record_uid = record.affidavit_uid_string

    sourcepdf_uid = sourcedoc_final.affidavit_uid_string

    pdf_string = ""

    pdf_record = PdfRecord.objects.filter(sourcedoc_link = sourcedoc_final)[0]

    '''Item 1. On April 17, 2006, Al Baraka Bank processed Payment Order FT224 transferring EUR

        7,100.00 (CDN $9,976.21) to Bachar El Ghussein. [BFG-1-SOURCE] These funds were recorded 

        in the 2006 accounting of NA Solid Petroserve Ltd.'s Tunisian Branch with journal entry 474 as 

        having been sent to Fluid Control Europe. [BFG-1-ACCT]'''
    #corpus_include_fields = ["Month","Day","Year","Amount","Currency","Company","Piece_Number","Document_Number","Source_Bank_Account","PurchaseOrder_Number","Cheque_Number","Address","City","Country","Telephone","Page_Number","Notes","Translation_Notes"]

    pdf_string += "Item #"+str(exhibit_count)+". "+str(doctype_pretty_name)+":"
    pdf_string += "\n"

    pdf_string += "    On "
    #On April 17, 2006, / On an unknown Date,
    pdf_string = test_length_add_line(pdf_string, test_icr_content("IssueDate",record))

    pdf_string += " "
    
    pdf_string = test_length_add_line(pdf_string, "a "+doctype_pretty_name+" document of number ")
    

    # X Document_Number / unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Document_Number",record))
    pdf_string = test_length_add_line(pdf_string, " and piece number ")
    
    
    
    # X Piece Number/ unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Piece_Number",record))
    pdf_string = test_length_add_line(pdf_string, " was processed, transferring ")

    

    # X Amount/ an unknown Amount
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Amount",record))
    pdf_string = test_length_add_line(pdf_string, " of Currency ")
    
    
    # X Currency/ unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Currency",record))
    pdf_string = test_length_add_line(pdf_string, " to ")
    
  
    # X Company / an unknown Recipient
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Company",record))
    pdf_string = test_length_add_line(pdf_string, ", with Address ")
    
    
    # X Address / unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Address",record))
    pdf_string = test_length_add_line(pdf_string, " and Phone Number ")
    
    
    # X Telephone / unknown
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Telephone",record))
    pdf_string = test_length_add_line(pdf_string, " residing in ")
    
    
    # X City, Country / an unknown Location
    pdf_string = test_length_add_line(pdf_string, test_icr_content("Location",record))
    pdf_string += ". "
    


    # Extra fields: Cheque Number, Purchase Order Number, Source Bank Account
    
    pdf_string += '\n'
    pdf_string += '\n'
    pdf_string = test_length_add_line(pdf_string, "    In Directory ")
    pdf_string = test_length_add_line(pdf_string, test_sourcepdfs_content("JobDirectory",sourcedoc_final))
    pdf_string = test_length_add_line(pdf_string, " with Filename ")
    pdf_string = test_length_add_line(pdf_string, test_sourcepdfs_content("Filename",sourcedoc_final))
    pdf_string += '.'
    
    pdf_string += "\n\n     "
    
    # [icr_uid]

    pdf_string = test_length_add_line(pdf_string, "Associated ICR Document UID: ["+test_sourcepdfs_content("icr_uid",record)+"]")
    
    pdf_string += "\n     "
    
    pdf_string = test_length_add_line(pdf_string, "SRC Item Reference UID: ["+str(sourcepdf_uid)+"]")

    return_string = pdf_string

    return return_string


def test_grandelivre_content(field_name,record):

    actual_content = ""
    
    if field_name == "IssueDate":
        try:
            
            day_bool = False
            if record.Day != "NaN" and record.Day != "" and record.Day != "*":
                day_string = str(record.Day)
                day_bool = True
            else:
                day_string = "an unknown Day"
                
            month_bool = False
            if record.Month != "NaN" and record.Month != "" and record.Month != "*":
                
                try:
                
                    month_string = Month_Dictionary[str(record.Month)]
                    
                except:
                
                    month_string = str(record.Month)
                    
                month_bool = True
            else:
                month_string = "an unknown Month"
                
            year_bool = False
            if record.Year != "NaN" and record.Year != "" and record.Year != "*":
                year_string = str(record.Year)
                year_bool = True
            else:
                year_string = "an unknown Year"

            actual_content = month_string + " " + day_string + ", " + year_string
        
        
            if not day_bool and not month_bool and not year_bool:
                
                actual_content = "an unknown Date, "
            
        except:
        
            actual_content = "an unknown Date, "
    
    if field_name == "BankName":
        try:
            field_content = str(record.BankName)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content +" Bank"

            else:
            
                actual_content = "an unknown Bank"
        except:
        
            actual_content = "an unknown Bank"
    

    if field_name == "Credit":
        try:
            field_content = str(record.Credit)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "0"
        except:
        
            actual_content = "0"
    
    if field_name == "Debit":
        try:
            field_content = str(record.Debit)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "0"
        except:
        
            actual_content = "0"
    
    if field_name == "NoMvt":
        try:
            field_content = str(record.NoMvt)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
    
    if field_name == "BankCurrency":
        try:
            field_content = str(record.BankCurrency)
        
            if field_content !="" and field_content != "no" and field_content != " " and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "an unknown Currency"
         
        except:
        
            actual_content = "an unknown Currency"
            

    if field_name == "BankAccount":
        try:
            field_content = str(record.BankAccount)

            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = "'"+field_content+"'"

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
            
    if field_name == "ExtraFields":
        
        try:
        
            accountnum_string = str(record.AccountNum)
            company_string = str(record.Company)
            journal_string = str(record.Journal)
            nopiece_string = str(record.NoPiece)
            
            field_content = accountnum_string
            
            if field_content !="" and field_content != "no" and field_content != "*":

                accountnum_string = "      Account Number is '" + field_content + "'.\n"
                accountnum = True
        

            else:

                accountnum = False
                accountnum_string = ""
            
            
            field_content = company_string
            
            if field_content !="" and field_content != "no" and field_content != "*":

                company_string = "      Company is " + field_content + ".\n"
                company = True

            else:
            
                company = False
                company_string = ""
                
        
            field_content = journal_string
            
            if field_content !="" and field_content != "no" and field_content != "*":
           
                journal_string = "      Journal is : ' "+field_content + "'.\n"
                journal = True

            else:
            
                journal = False
                journal_string = ""   
            
            field_content = nopiece_string
            
            if field_content !="" and field_content != "no" and field_content != "*":
           
                nopiece_string = "      Piece Number is : ' "+field_content + "'.\n    "
                nopiece = True

            else:
            
                nopiece = False
                nopiece_string = "" 
            
            
            if accountnum == True or company == True or journal == True or nopiece == True:

                actual_content = "\n    Extra information: \n" + accountnum_string + company_string + journal_string + nopiece_string
                
        except:

            actual_content = ""

    return actual_content
    
def add_grandelivre_entry_content(exhibit_count, record):


    return_string = ""

    record_uid = record.affidavit_uid_string


    pdf_string = ""
    
    '''    
    Item 1.
    
       On April 17, 2006, (Issuedate), NA Solid Petroserve Internal Account Records account for a transfer, Movement Number 174 (NoMvt), of 7000(Credit)/6000(Debit)
       of Currency USD (BankCurrency).

       Extra Fields(ExtraFields):
       
           -The Account Number is 578 (AccountNum).
           -The Jou is 745 (Journal).
           -The Company is 745 (Company).
           -The Piece Number is 158 (NoPiece).
    
    '''


    pdf_string += "Item #"+str(exhibit_count)+":"
    pdf_string += "\n"

    pdf_string += "    On "
    #On April 17, 2006, / On an unknown Date,
    pdf_string = test_length_add_line(pdf_string, test_grandelivre_content("IssueDate",record))
    pdf_string = test_length_add_line(pdf_string, " NA Solid Petroserve Internal Account Records account for a transfer,")
    pdf_string = test_length_add_line(pdf_string, " journal entry ")
    
    # X BankName Bank/ an unknown Bank
    pdf_string = test_length_add_line(pdf_string, test_grandelivre_content("NoMvt",record))
    pdf_string = test_length_add_line(pdf_string, ", of ")
    # X Reference / unknown
    pdf_string = test_length_add_line(pdf_string, test_grandelivre_content("Credit",record))
    pdf_string = test_length_add_line(pdf_string, " Credit/")
    # X Amount/ an unknown Amount
    pdf_string = test_length_add_line(pdf_string, test_grandelivre_content("Debit",record))
    pdf_string = test_length_add_line(pdf_string, " Debit of ")
    
    # X BankCurrency/ unknown
    pdf_string = test_length_add_line(pdf_string, test_grandelivre_content("BankCurrency",record)+".")
    
    
    # Extra fields: AccountNum, Journal, Company, Piece Number
    
    pdf_string = test_length_add_line(pdf_string, test_grandelivre_content("ExtraFields",record))
    
    
    pdf_string += "\n     "
    
    pdf_string = test_length_add_line(pdf_string, "GRLV Item Reference UID: ["+str(record_uid)+"]")

    return_string = pdf_string

    return return_string
    
def test_albaraka_content(field_name,record):

    actual_content = ""
    
    if field_name == "IssueDate":
        try:
            
            day_bool = False
            if record.PostDay != "NaN" and record.PostDay != "" and record.PostDay != "*":
                day_string = str(record.PostDay)
                day_bool = True
            else:
                day_string = "an unknown Day"
                
            month_bool = False
            if record.PostMonth != "NaN" and record.PostMonth != "" and record.PostMonth != "*":
                
                try:
                
                    month_string = Month_Dictionary[str(record.PostMonth)]
                    
                except:
                
                    month_string = str(record.PostMonth)
                    
                month_bool = True
            else:
                month_string = "an unknown Month"
                
            year_bool = False
            if record.PostYear != "NaN" and record.PostYear != "" and record.PostYear != "*":
                year_string = str(record.PostYear)
                year_bool = True
            else:
                year_string = "an unknown Year"

            actual_content = month_string + " " + day_string + ", " + year_string
        
        
            if not day_bool and not month_bool and not year_bool:
                
                actual_content = "an unknown Date, "
            
        except:
        
            actual_content = "an unknown Date, "
    
    if field_name == "BankName":
        try:
            field_content = str(record.BankName)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content +" Bank"

            else:
            
                actual_content = "an unknown Bank"
        except:
        
            actual_content = "an unknown Bank"
    
    if field_name == "Reference":
        try:
            field_content = str(record.Reference)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = "'"+field_content +"'"

            else:
            
                actual_content = "an unknown Bank"
        except:
        
            actual_content = "unknown"

    if field_name == "Amount":
        try:
            field_content = str(record.Amount)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "an unknown Amount"
        except:
        
            actual_content = "an unknown Amount"
            
    if field_name == "BankCurrency":
        try:
            field_content = str(record.BankCurrency)
        
            if field_content !="" and field_content != "no" and field_content != " " and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
         
        except:
        
            actual_content = "unknown"
            

    if field_name == "BankAccount":
        try:
            field_content = str(record.BankAccount)

            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = "'"+field_content+"'"

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
            
    if field_name == "ExtraFields":
    
        try:
        
            reftran_string = str(record.Reftran)
            libelle_string = str(record.Libelle)
            libdesc_string = str(record.Libdesc)
            provenance_string = str(record.Provenance)
            description_string = str(record.Description)
            
            field_content = reftran_string
            
            if field_content !="" and field_content != "no" and field_content != "*":
           
                reftran_string = "      Reftran is '" + field_content + "'.\n"
                reftran = True

            else:
            
                reftran = False
                reftran_string = ""
            
            field_content = libelle_string
            
            if field_content !="" and field_content != "no" and field_content != "*":
           
                libelle_string = "      Libelle is " + field_content + ".\n"
                libelle = True

            else:
            
                libelle = False
                libelle_string = ""

            field_content = provenance_string
            
            if field_content !="" and field_content != "no" and field_content != "*":
           
                provenance_string = "      Provenance is : ' "+field_content + "'.\n"
                provenance = True

            else:
            
                provenance = False
                provenance_string = ""   
            
            field_content = description_string
            
            if field_content !="" and field_content != "no" and field_content != "*":
           
                description_string = "      Description contains : ' "+field_content + "'.\n    "
                description = True

            else:
            
                description = False
                description_string = "" 

            if reftran == True or libelle == True or provenance == True or description == True:
         
                actual_content = "\n    Extra information: \n" + reftran_string + libelle_string + provenance_string + description_string
                
        except:

            actual_content = ""

    return actual_content
    
def add_albaraka_entry_content(exhibit_count, record):


    return_string = ""

    record_uid = record.affidavit_uid_string


    pdf_string = ""
    
    '''    
    Item 1.
    
       On April 17, 2006, (Issuedate), Al Baraka Bank (BankName) processed a transfer, Reference 174 (Reference), of 7000 (Amount)
       of Currency USD (BankCurrency).

       Extra Fields:
       
           -The Reftran is 578 (Reftran).
           -The Libelle is u28 (Libelle).
           -The Libdesc is 745 (Libdesc).
           -The Provenance is 745 (Provenance).
           -The Description contains 'lalala' (Description).
    
    '''


    pdf_string += "Item #"+str(exhibit_count)+":"
    pdf_string += "\n"

    pdf_string += "    On "
    #On April 17, 2006, / On an unknown Date,
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("IssueDate",record))

    # X BankName Bank/ an unknown Bank
    pdf_string = test_length_add_line(pdf_string, " ")
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("BankName",record))
    pdf_string = test_length_add_line(pdf_string, " processed a transfer, Reference ")
    # X Reference / unknown
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("Reference",record))
    pdf_string = test_length_add_line(pdf_string, ", of ")
    # X Amount/ an unknown Amount
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("Amount",record))
    pdf_string = test_length_add_line(pdf_string, " of Currency ")
    
    # X BankCurrency/ unknown
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("BankCurrency",record))
    pdf_string = test_length_add_line(pdf_string, " to Account ")
    # X BankAccount/ unknown
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("BankAccount",record)+".")

    # Extra fields: NoMvt, Lett, Memo
    
    pdf_string = test_length_add_line(pdf_string, test_albaraka_content("ExtraFields",record))
    
    pdf_string += "\n     "
    
    pdf_string = test_length_add_line(pdf_string, "ALBK Item Reference UID: ["+str(record_uid)+"]")

    return_string = pdf_string

    return return_string
    
def test_transactions_content(field_name,record):

    actual_content = ""
    
    if field_name == "IssueDate":
        try:
            
            day_bool = False
            if record.PostDay != "NaN" and record.PostDay != "" and record.PostDay != "*":
                day_string = str(record.PostDay)
                day_bool = True
            else:
                day_string = "an unknown Day"
                
            month_bool = False
            if record.PostMonth != "NaN" and record.PostMonth != "" and record.PostMonth != "*":
                
                try:
                
                    month_string = Month_Dictionary[str(record.PostMonth)]
                    
                except:
                
                    month_string = str(record.PostMonth)
                    
                month_bool = True
            else:
                month_string = "an unknown Month"
                
            year_bool = False
            if record.PostYear != "NaN" and record.PostYear != "" and record.PostYear != "*":
                year_string = str(record.PostYear)
                year_bool = True
            else:
                year_string = "an unknown Year"

            actual_content = month_string + " " + day_string + ", " + year_string
        
        
            if not day_bool and not month_bool and not year_bool:
                
                actual_content = "an unknown Date, "
            
        except:
        
            actual_content = "an unknown Date, "
    
    if field_name == "BankName":
        try:
            field_content = str(record.BankName)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content +" Bank"

            else:
            
                actual_content = "an unknown Bank"
        except:
        
            actual_content = "an unknown Bank"
    
    if field_name == "Reference":
        try:
            field_content = str(record.Reference)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = "'"+field_content +"'"

            else:
            
                actual_content = "an unknown Bank"
        except:
        
            actual_content = "unknown"

    if field_name == "Amount":
        try:
            field_content = str(record.Amount)
        
            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "an unknown Amount"
        except:
        
            actual_content = "an unknown Amount"
            
    if field_name == "BankCurrency":
        try:
            field_content = str(record.BankCurrency)
        
            if field_content !="" and field_content != "no" and field_content != " " and field_content != "*":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
         
        except:
        
            actual_content = "unknown"
            

    if field_name == "BankAccount":
        try:
            field_content = str(record.BankAccount)

            if field_content !="" and field_content != "no" and field_content != "*":
           
                actual_content = "'"+field_content+"'"

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
    

    
    if field_name == "DocType":
        try:
            field_content = str(record.BestIcrMatch.modified_document_type.pretty_name)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "a Document"
        except:
        
            actual_content = "a Document"
    
    if field_name == "Document_Number":
        try:
            field_content = str(record.BestIcrMatch.ocrrecord_link.Document_Number)
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
    
    if field_name == "icr_uid":
        try:
            field_content = str(record.BestIcrMatch.affidavit_uid_string)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "No_Linked_Entry"
        except:
        
            actual_content = "No_Linked_Entry"
    
    if field_name == "sourcepdf_uid":
        try:
            field_content = str(record.BestIcrMatch.sourcedoc_link.affidavit_uid_string)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "No_Linked_SourceDoc"
        except:
        
            actual_content = "No_Linked_SourceDoc"
    
    #In the following ones, the "record" being received is an Internal Record, not an Icr
    if field_name == "LedgerYear":
        try:
            field_content = str(record.LedgerYear)
        
            if field_content != "None" and field_content !="" and field_content !="*":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
    
    if field_name == "NoPiece":
        try:
            field_content = str(record.NoPiece)
        
            if field_content != "None" and field_content !="" and field_content !="*":
           
                actual_content = field_content

            else:
            
                actual_content = "unknown"
        except:
        
            actual_content = "unknown"
    
    if field_name == "Company":
        try:
            field_content = str(record.Company)
        
            if field_content != "None" and field_content !="" and field_content !="*":
           
                actual_content = field_content

            else:
            
                actual_content = "an unknown Recipient"
        except:
        
            actual_content = "an unknown Recipient"
    
    if field_name == "grandelivre_uid":
        try:
            field_content = str(record.affidavit_uid_string)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "No_Linked_Int.Record"
        except:
        
            actual_content = "No_Linked_Int.Record"

    if field_name == "albaraka_uid":
        try:
            field_content = str(record.affidavit_uid_string)
        
            if field_content != "None" and field_content !="":
           
                actual_content = field_content

            else:
            
                actual_content = "No_Linked_Bank_Record"
        except:
        
            actual_content = "No_Linked_Bank_Record"
            
    if field_name == "Libdesc":
        try:
            field_content = str(record.Libdesc)
        
            if field_content == "GLCANCELLEDCHEQUES":
           
                actual_content = "    Note: The extended date range of this records is due to a cancellation/adjustment\n    of Cheques."

            else:
            
                actual_content = ""
        except:
        
            actual_content = ""
            
    return actual_content
    
def add_transactions_entry_content(exhibit_count, record):


    return_string = ""

    record_uid = record.affidavit_uid_string

    pdf_string = ""
    
    '''Item 1. On April 17, 2006, Al Baraka Bank processed Payment Order FT224 transferring EUR

        7,100.00 (CDN $9,976.21) to Bachar El Ghussein. [BFG-1-ICR] (icr_uid) [BFG-1-SOURCE] (sourcepdf_uid) These funds were recorded 

        in the following 2006 (LedgerYear) accounting of NA Solid Petroserve Ltd.'s Tunisian Branch records: 
        
        - Journal entry 474 (NoPiece), sent to Fluid Control Europe (Company). [BFG-1-ACCT] (grandelivreh_uid)
        - Journal entry 475 (NoPiece), sent to Fluid Control Europe (Company). [BFG-1-ACCT] (grandelivreh_uid)
        - Journal entry 476 (NoPiece), sent to Fluid Control Europe (Company). [BFG-1-ACCT] (grandelivreh_uid)'''
        

    '''pdf_string += "Item #"+str(exhibit_count)+". ["+str(record_uid)+"]"+":"
    pdf_string += "\n"

    pdf_string += "    On "
    #On April 17, 2006, / On an unknown Date,
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("IssueDate",record))

    # X BankName Bank/ an unknown Bank
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("BankName",record))
    pdf_string = test_length_add_line(pdf_string, " processed ")
    
    # X DocType/ a Document
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("DocType",record))
    pdf_string = test_length_add_line(pdf_string, " with Document Number ")
    
    # X Document_Number/ unknown
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("Document_Number",record))
    pdf_string = test_length_add_line(pdf_string, " transferring ")
    
    
    # X Amount/ an unknown Amount
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("Amount",record))
    pdf_string = test_length_add_line(pdf_string, " of Currency ")
    
    # X BankCurrency/ unknown
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("BankCurrency",record))
    pdf_string = test_length_add_line(pdf_string, " to Account ")
    # X BankAccount/ unknown
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("BankAccount",record)+".")
    
    pdf_string += "\n    "
    
    # [icr_uid]

    pdf_string = test_length_add_line(pdf_string, "Extracted Data UID: ["+test_transactions_content("icr_uid",record)+"]")
    
    pdf_string += "\n    "
    
    # [sourcepdf_uid]

    pdf_string = test_length_add_line(pdf_string, "Associated Document UID: ["+test_transactions_content("sourcepdf_uid",record)+"]")
    
    pdf_string += "\n"
    
    # X Libdesc ## This is an special case, look up the code in the function
    pdf_string = test_length_add_line(pdf_string, test_transactions_content("Libdesc",record))
        
    # Extra fields: NoMvt, Lett, Memo
        
    #pdf_string = test_length_add_line(pdf_string, test_transactions_content("ExtraFields",record))'''
    
    pdf_string = record.AffidavitString

    return_string = pdf_string

    return return_string

def prepareAffidavitString(transaction_item,count):
      
    affi_date = ""
    affi_amount = ""
    affi_company = ""
    
    all_dates =  []
    all_dates.append(transaction_item.CompletePostDate)
    all_dates.append(transaction_item.CompleteValueDate)
    
    for internal in transaction_item.internal_records_list.all():
        all_dates.append(internal.Day+"/"+internal.Month+"/"+internal.Year)
    for bankrecord in transaction_item.bank_records_list.all():
        all_dates.append(bankrecord.ValueDay+"/"+bankrecord.ValueMonth+"/"+bankrecord.ValueYear)
        all_dates.append(bankrecord.PostDay+"/"+bankrecord.PostMonth+"/"+bankrecord.PostYear)
    
    if len(all_dates)>0:
        all_dates.sort(reverse=True)
        affi_date = all_dates[0]
        
    affi_amount = transaction_item.Amount + " " + transaction_item.BankCurrency
    
    #print "----> "+transaction_item.Libdesc+" <-----"
    legend = TransactionLegend.objects.get(ReferenceType = transaction_item.Libdesc)
    
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
    
    if "(0)" in affi_final:
        affi_final = affi_final.replace("(0)","#"+str(count))
    
    if "(1)" in affi_final:
    
        affi_final = affi_final.replace("(1)",affi_date)
        
    if "(2)" in affi_final:
    
        affi_final = affi_final.replace("(2)",affi_amount)
        
    if "(3)" in affi_final:
    
        affi_final = affi_final.replace("(3)",affi_company)
        
    if "(JUMP)" in affi_final:
        
            affi_final = affi_final.replace("(JUMP)","\n     ")    
    transaction_item.AffidavitString = affi_final
    transaction_item.save()
    
def add_transactions_entry_content_internal(record):

    return_string = ""
    
    pdf_string = ""
    
    internal_records = record.internal_records_list.all()
    
    if len(internal_records) == 0:
    
        pdf_string += "\n"
        
        pdf_string = test_length_add_line(pdf_string, "     There were no internal accounting records found linking to this data. ")
    
    else:
    
        pdf_string += "\n"
    
        pdf_string = test_length_add_line(pdf_string, "    These funds were recorded in the following accounting records of NA Solid Petroserve Ltd.'s Tunisian Branch:")

        pdf_string += "\n"
        
        with transaction.commit_on_success():
            for int_record in internal_records:
        
                pdf_string += "\n      -"
                # X LedgerYear/ unknown
                pdf_string = test_length_add_line(pdf_string, test_transactions_content("LedgerYear",int_record)+" Ledger,")
                pdf_string = test_length_add_line(pdf_string, " journal entry " )
    
                # X NoPiece/ unknown
                pdf_string = test_length_add_line(pdf_string, test_transactions_content("NoPiece",int_record)+".")
                                
                pdf_string += "\n            "
    
                # [icr_uid]

                pdf_string = test_length_add_line(pdf_string, "GRLV Record Reference UID: ["+test_transactions_content("grandelivre_uid",int_record)+"]")
                
    return_string = pdf_string
    
    return return_string
    
def add_transactions_entry_content_albaraka(record):

    return_string = ""
    
    pdf_string = ""
    
    bank_records = record.bank_records_list.all()
    
    if len(bank_records) == 0:
    
        pdf_string += "\n\n"
        
        pdf_string = test_length_add_line(pdf_string, "     There were no bank records found linking to this data. ")
    
    else:
    
        pdf_string += "\n\n"
    
        pdf_string = test_length_add_line(pdf_string, "    These are the references of the Bank Records (ALBK) related to this transaction:")

        pdf_string += "\n"
        
        with transaction.commit_on_success():
            for bank_record in bank_records:
        
                pdf_string += "\n            "
        
                pdf_string = test_length_add_line(pdf_string, "ALBK Record Reference UID: ["+test_transactions_content("albaraka_uid",bank_record)+"]")
                
    return_string = pdf_string
    
    return return_string