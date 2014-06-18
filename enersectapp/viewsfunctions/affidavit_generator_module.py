
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

Month_Dictionary = {"01":"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"December"}
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
    
    corpus_list = ["icr","sourcepdfs","grandelivre","albaraka","transactions"]
    
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
        
        if "icr" in file:
            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            icr_corpus_contents_list.append(file_dict)
            
        if "sourcepdfs" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            sourcepdfs_corpus_contents_list.append(file_dict)
            
        if "grandelivre" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            grandelivre_corpus_contents_list.append(file_dict)
            
        if "albaraka" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            albaraka_corpus_contents_list.append(file_dict)
            
        if "transactions" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            transactions_corpus_contents_list.append(file_dict)
            
            
            
    icr_corpus_dict["corpus_name"] = "icr"
    icr_corpus_dict["corpus_contents"] = icr_corpus_contents_list
    
    sourcepdfs_corpus_dict["corpus_name"] = "sourcepdfs"
    sourcepdfs_corpus_dict["corpus_contents"] = sourcepdfs_corpus_contents_list
    
    grandelivre_corpus_dict["corpus_name"] = "grandelivre"
    grandelivre_corpus_dict["corpus_contents"] = grandelivre_corpus_contents_list
    
    albaraka_corpus_dict["corpus_name"] = "albaraka"
    albaraka_corpus_dict["corpus_contents"] = albaraka_corpus_contents_list
    
    transactions_corpus_dict["corpus_name"] = "transactions"
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
    
    if "icr" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("icr","cover")
        delete_temp_affidavit_files("icr","partial")
        delete_temp_affidavit_files("icr","merge")
        
        generate_icr_output(request,watermark_name)
        
    
    if "sourcepdfs" in documents_corpus_to_include_in_output:
        
        try:
            complete_corpus_mark = request.POST['complete_corpus_mark']
        except:
            complete_corpus_mark = ""
        
        if complete_corpus_mark != "complete":
        
            delete_temp_affidavit_files("sourcepdfs","cover")
            delete_temp_affidavit_files("sourcepdfs","partial")
            delete_temp_affidavit_files("sourcepdfs","merge")
        
        generate_sourcepdfs_output(request,watermark_name)
        
    if "grandelivre" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("grandelivre","cover")
        delete_temp_affidavit_files("grandelivre","partial")
        delete_temp_affidavit_files("grandelivre","merge")
        
        generate_grandelivre_output(request,watermark_name)
        
    if "albaraka" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("albaraka","cover")
        delete_temp_affidavit_files("albaraka","partial")
        delete_temp_affidavit_files("albaraka","merge")
        
        generate_albaraka_output(request,watermark_name)
        
    if "transactions" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("transactions","cover")
        delete_temp_affidavit_files("transactions","partial")
        delete_temp_affidavit_files("transactions","merge")
        
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
    

    temp_filename = "legaldiscoverytemp/output_files/"+"icr"+"/"+"icr__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

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
                
                temp_filename = "legaldiscoverytemp/output_files/"+"icr"+"/"+"icr__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                did_page_jump = True
                
                db.reset_queries()
                
                pdf_string = ""

            if did_page_jump == True:
                      

                    pdf_string = ""
                    pdf_string += "                                                                                                                                 "+"icr__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
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
                    pdf_string += "                                                                                                                                 "+"icr__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
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

        temp_filename = "legaldiscoverytemp/output_files/"+"icr"+"/"+"icr__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
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
        
        temp_filename = "legaldiscoverytemp/output_files/"+"sourcepdfs"+"/"+"sourcepdfs__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

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
 
        corpus_type = "sourcepdfs"

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
                
                temp_filename = "legaldiscoverytemp/output_files/"+"sourcepdfs"+"/"+"sourcepdfs__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
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
            pdf_string += "                                                                                                                    "+"sourcepdfs__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
            pdf_string +="\n\n\n"
            page_count +=1
             
            pdf_string += "Exhibit #"+str(exhibit_count)+" , UID: "+str(record_uid)+", "+str(doctype_name)+":"
            pdf_string += "\n"
            pdf_string += "\n"
            
                        
            pdf_string += ".  - File Name is: "+str(filename)+", on Directory: "+str(job_directory)
            
            
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
    
        temp_filename = "legaldiscoverytemp/output_files/"+"sourcepdfs"+"/"+"sourcepdfs__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
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
    

    temp_filename = "legaldiscoverytemp/output_files/"+"grandelivre"+"/"+"grandelivre__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

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
                
                temp_filename = "legaldiscoverytemp/output_files/"+"grandelivre"+"/"+"grandelivre__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            if (doc_iterator % docs_per_pdf == 0 or doc_iterator == 0) and did_page_jump == False:
       
                pdf_string = ""
                pdf_string += "                                                                                                                    "+"grandelivre__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                pdf_string +="\n\n\n"
                page_count +=1    
                
            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["IssueDate","Credit","Piece_Number","Day","Month","Year","NoPiece","ExchangeRate","Company","AccountNum","NoMvt","Memo","Lett","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["IssueDate","Credit","Piece_Number","Day","Month","Year","NoPiece","ExchangeRate","Company","AccountNum","NoMvt","Memo","Lett","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = InternalRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                record_uid = record.affidavit_uid_string
                
                pdf_string += "Exhibit #"+str(exhibit_count)+" , UID: "+str(record_uid)+":"
                pdf_string += "\n"
                pdf_string += "\n"
                
                show_date = str(record.Day)+"/"+str(record.Month)+"/"+str(record.Year)
                if show_date == "XX/XX/XXXX" or show_date == "":
                    show_date = "(No Date)"
                show_amount = record.Credit    
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
                            
                            if (len(pdf_string.split("\n")[-1]) + len(" "+field_name+" "+field_content)) > max_characters_line:
                                test_string = "\n"
                                test_string2 = ".              -"
                            else:
                                test_string = ""
                                test_string2 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content !="None" and field_content != "*":
                                pdf_string += " "+test_string+test_string2+field_name+" "+field_content
                              
                        except:
                            test_string = ""
                        
                    except:
                        pdf_string += " "
                        
                
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
                    pdf_string += "                                                                                                                    "+"grandelivre__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
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

        temp_filename = "legaldiscoverytemp/output_files/"+"grandelivre"+"/"+"grandelivre__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
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
    

    temp_filename = "legaldiscoverytemp/output_files/"+"albaraka"+"/"+"albaraka__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

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
                

            if (doc_iterator % docs_per_pdf == 0 or doc_iterator == 0) and did_page_jump == False:
    
    
                pdf_string = ""
                pdf_string += "                                                                                                                      "+"albaraka__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                pdf_string +="\n\n\n"
                page_count +=1

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                print "---------"+str("albaraka")+"--------"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"albaraka"+"/"+"albaraka__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["Amount","PostDay","PostMonth","PostYear","ValueDay","ValueMonth","ValueYear","Libelle","Reference","Description","TransactionId","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["Amount","PostDay","PostMonth","PostYear","ValueDay","ValueMonth","ValueYear","Libelle","Reference","Description","TransactionId","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = BankRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                record_uid = record.affidavit_uid_string
                
                pdf_string += "Exhibit #"+str(exhibit_count)+" , UID: "+str(record_uid)+":"
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
                            
                            if (len(pdf_string.split("\n")[-1]) + len(" "+field_name+" "+field_content)) > max_characters_line:
                                test_string = "\n"
                                test_string2 = ".              -"
                            else:
                                test_string = ""
                                test_string2 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content !="None" and field_content != "*":
                                pdf_string += " "+test_string+test_string2+field_name+" "+field_content
                              
                        except:
                            test_string = ""
                        
                    except:
                        pdf_string += " "
                        
                
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

                    pdf_string += "                                                                                                                      "+"albaraka__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
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

        temp_filename = "legaldiscoverytemp/output_files/"+"albaraka"+"/"+"albaraka__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
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
    

    temp_filename = "legaldiscoverytemp/output_files/"+"transactions"+"/"+"transactions__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

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
                print "---------"+str("transactions")+"--------"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"transactions"+"/"+"transactions__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        
            if (doc_iterator % docs_per_pdf == 0 or doc_iterator == 0) and did_page_jump == False:
            
                pdf_string += "                                                                                                                  "+"transactions__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                pdf_string +="\n\n\n"
                page_count +=1
                
            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["NumberBankRecordIndexes","BankRecordsUIDArray","NumberInternalRecordIndexes","InternalRecordUIDArray","CompletePostDate","CompleteValueDate","DateDiscrepancy","Amount","AmountDiscrepancy","ValueYear","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["NumberBankRecordIndexes","BankRecordsUIDArray","NumberInternalRecordIndexes","InternalRecordUIDArray","CompletePostDate","CompleteValueDate","DateDiscrepancy","Amount","AmountDiscrepancy","ValueYear","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = TransactionTable.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                record_uid = record.affidavit_uid_string
                
                pdf_string += "Exhibit #"+str(exhibit_count)+" , UID: "+str(record_uid)+":"
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
                                    corpus_tempname = "albaraka"
                                else:
                                    corpus_tempname = "grandelivre"
                            
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
                                            pdf_string += "                                                                                                                  "+"transactions__"+str(watermark_name)+"__page__"+str(page_count).zfill(10)
                                            pdf_string +="\n\n\n"
                                            pdf_string += temp_str
                                            page_count +=1

                                            did_page_jump = True
                                
                              
                        except:
                            test_string = ""
                        
                    except:
                        pdf_string += " "
                        
                
                '''Write command to output the existing pdf_string variable as a new row, then line break'''
                
                pdf_string += '\n'
                pdf_string += '\n'
                
                '''if pdf_string.count('\n') > 45:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""

                    did_page_jump = True'''
                    
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

        temp_filename = "legaldiscoverytemp/output_files/"+"transactions"+"/"+"transactions__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
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
     
    corpus_icr = PdfRecord.objects.filter(audit_mark = "None").exclude(EntryByCompany__name = "TestGroup").exclude(EntryAuthor__username = "nemot").exclude(sourcedoc_link__corrupt = "yes").order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day').distinct()
    
    #corpus_sourcepdfs will be represented in the corpus_icr loop, by the field sourcedoc_link
    #corpus_sourcepdfs = SourcePdf.objects.all().distinct()

    corpus_grandelivre = InternalRecord.objects.all().order_by('Year','Month','Day').distinct()

    corpus_albaraka = BankRecord.objects.all().order_by('ValueYear','ValueMonth','ValueDay').distinct()

    corpus_transactions = TransactionTable.objects.all().order_by('ValueYear','ValueMonth','ValueDay').distinct()

    with transaction.commit_on_success():
        
        db.reset_queries()
        
        corpus_tag = "icr"
        corpus_tag2 = "sourcepdfs"
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
    
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)

            
        
    with transaction.commit_on_success():
        
        db.reset_queries()
        
        corpus_tag = "grandelivre"
        corpus_doccount = 1
    
    
        for element in corpus_grandelivre:
        
            element.affidavit_watermark_string = watermark_name
            #element.actual_affidavit_watermark = watermark_instance
            element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + str(corpus_doccount).zfill(7) 

            element.save()
            
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)+"----> PK : "+str(element.pk)
            
              
    
    with transaction.commit_on_success():
    
        db.reset_queries()
        
        corpus_tag = "albaraka"   
        corpus_doccount = 1  
    
        for element in corpus_albaraka:
        
            element.affidavit_watermark_string = watermark_name
            #element.actual_affidavit_watermark = watermark_instance
            element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + str(corpus_doccount).zfill(7) 

            element.save()
            
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)
        
        
    
    with transaction.commit_on_success():
    
        db.reset_queries()
        
        corpus_tag = "transactions"
        corpus_doccount = 1
    
        for element in corpus_transactions:
        
            element.affidavit_watermark_string = watermark_name
            #element.actual_affidavit_watermark = watermark_instance
            element.affidavit_uid_string = corpus_tag + "__" + str(watermark_name) + "__element__" + str(corpus_doccount).zfill(7) 
    
            element.BankRecordsUIDArray = str(element.bank_records_list.all().values_list('affidavit_uid_string',flat=True)).replace("albaraka" + "__" + str(watermark_name) + "__element__","").replace("u","").replace("'","").replace("[","").replace("]","")
            
            element.InternalRecordUIDArray = str(element.internal_records_list.all().values_list('affidavit_uid_string',flat=True)).replace("grandelivre" + "__" + str(watermark_name) + "__element__","").replace("u","").replace("'","").replace("[","").replace("]","")   
            
            element.save()
            
            corpus_doccount += 1
            print "---->"+str(corpus_tag)+"--->"+str(corpus_doccount)
    


    
def delete_temp_affidavit_files(corpus,partial_or_merge):

    corpus_list = ["icr","sourcepdfs","grandelivre","albaraka","transactions"]

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
                
                actual_content = "an unknown Date"
        except:
        
            actual_content = "an unknown Date"
    
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
        
            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content != "no" and field_content != "Blank":
           
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

    pdf_string += "Item #"+str(exhibit_count)+". ["+str(record_uid)+"], "+str(doctype_pretty_name)+":"
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
    
    
    # [sourcepdf_uid]

    pdf_string = test_length_add_line(pdf_string, "Associated Document UID: ["+test_icr_content("sourcepdf_uid",record)+"]")

    

    return_string = pdf_string

    return return_string