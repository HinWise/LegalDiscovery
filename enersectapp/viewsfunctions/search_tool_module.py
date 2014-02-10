
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection

from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

from pyPdf import PdfFileWriter, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO


from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


import random

def search_tool(request):
    
    the_user = request.user
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    if len(the_user.groups.filter(name="TeamLeaders")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
        
    else:
    
        user_type = "user"

    ###COMMON BLOCK###    
    
    #word = p.pdf_searchword
    word="all"
    word_amount= ""
    word_amount_credit= ""
    word_amount_debit= ""
    word_companyname=""
    word_date=""
    word_docname=""
    word_id_docname=""
    word_accountnumber=""
    word_movnumber=""
    word_journal=""
    word_s=""
    word_lett=""
    word_id=""
    word_job_directory=""
    word_multipart_filename=""
    corpus_word=""
    filter_word = ""
    search_options = ""
    records_list=[]
    
    try:
        word_amount = request.POST['search_word_amount']
    except (KeyError):
        
        word_amount = ""
        
    try:
        word_amount_credit = request.POST['search_word_amount_credit']
    except (KeyError):
        
        word_amount_credit = ""
    
    try:
        word_amount_debit = request.POST['search_word_amount_debit']
    except (KeyError):
        
        word_amount_debit = ""
    
    try:
        word_amount = request.POST['search_word_amount']
    except (KeyError):
        
        word_amount = ""
    
    
    try:
        word_companyname = request.POST['search_word_companyname']
    except (KeyError):
        
        word_companyname=""
        
    try:
        word_date = request.POST['search_word_date']
    except (KeyError):
        
        word_date=""
    
    try:
        word_doctype = request.POST['search_word_doctype']
    except (KeyError):
        
        word_doctype=""
    
    try:
        word_piecenumber = request.POST['search_word_piecenumber']
    except (KeyError):
        
        word_piecenumber=""
    
    try:
        word_docname = request.POST['search_word_docname']
    except (KeyError):
        
        word_docname=""
    
    try:
        word_id_docname = request.POST['search_word_id_docname']
    except (KeyError):
        
        word_id_docname=""
    
    try:
        word_accountnumber = request.POST['search_word_accountnumber']
    except (KeyError):
        
        word_accountnumber=""
    
    try:
        word_movnumber = request.POST['search_word_movnumber']
    except (KeyError):
        
        word_movnumber=""
        
    try:
        word_journal = request.POST['search_word_journal']
    except (KeyError):
        
        word_journal=""
    
    try:
        word_s = request.POST['search_word_s']
    except (KeyError):
        
        word_s=""
        
    try:
        word_lett = request.POST['search_word_lett']
    except (KeyError):
        
        word_lett=""
        
    try:
        word_id = request.POST['search_word_id']
    except (KeyError):
        
        word_id=""
        
    try:
        word_job_directory = request.POST['search_job_directory']
    except (KeyError):
        
        word_job_directory=""
    
    try:
        word_multipart_filename = request.POST['search_word_multipart_filename']
    except (KeyError):
        
        word_multipart_filename=""
    
    try:
        corpus_word = request.POST['corpus_word']
    except (KeyError):
        
        corpus_word = "corpus_ocr_records"
    
    try:
        filter_word = request.POST['filter_word']
    except (KeyError):
        
        filter_word = "pdf_all"
    
    try:
        id_assign = request.POST['id_assign']
    except (KeyError):
        
        id_assign = "none"

        
    try:
        category_fields_order_list = request.POST['category_fields_order_list']
        category_fields_order_list = str(category_fields_order_list)
        
    except (KeyError):
        
        category_fields_order_list = ""
            
    
    #word = str(word)
    word_amount= str(word_amount).encode("utf8")
    word_amount_credit= str(word_amount_credit).encode("utf8")
    word_amount_debit= str(word_amount_debit).encode("utf8")
    word_companyname= word_companyname.encode("utf8")
    word_date= str(word_date).encode("utf8")
    word_doctype= str(word_doctype).encode("utf8")
    word_piecenumber= str(word_piecenumber).encode("utf8")
    word_docname= str(word_docname).encode("utf8")
    word_id_docname= str(word_id_docname).encode("utf8")
    word_accountnumber= str(word_accountnumber).encode("utf8")
    word_movnumber= str(word_movnumber).encode("utf8")
    word_journal= str(word_journal).encode("utf8")
    word_s= str(word_s).encode("utf8")
    word_lett= str(word_lett).encode("utf8")
    word_id= str(word_id).encode("utf8")
    word_job_directory= str(word_job_directory).encode("utf8")
    word_multipart_filename= str(word_multipart_filename).encode("utf8")
    filter_word = filter_word.lower()    
    corpus_word = corpus_word.lower()
    

    
    #DocTypes list for the Menu
    
    types_list = SourceDocType.objects.exclude(name="other").exclude(name="recuperation").exclude(name="blank probable").order_by('name')
    
    #Company Names list for the Menu
    
    companyname_list = CompanyTemplate.objects.all().order_by('companyname_base').values_list('companyname_base',flat=True).distinct()
    
    actual_min_num = 1
    
    try:
        prev_next_results = request.POST['prev_next_results']
        prev_next_results = str(prev_next_results)
    except (KeyError):
        
        prev_next_results = ""
        
    try:
        actual_min_num = request.POST['actual_min_num']
        actual_min_num = int(actual_min_num)
    except (KeyError):
        
        actual_min_num = 1
    
    

    if(prev_next_results == ""):
        actual_min_num = 0
    
    if(prev_next_results == "Prev"):
        actual_min_num -= 50
        
    if(prev_next_results == "Next"):
        actual_min_num += 50
        
    if(prev_next_results == "Update"):
        actual_min_num = actual_min_num
    
    if actual_min_num < 1:
    
        actual_min_num = 1
    
    
    max_num = actual_min_num + 50
    
    
    ###END OF COMMON BLOCK###  
    
    #Corpus block
    
    if corpus_word=="corpus_source_records":
    
        # If button "Assign to Group" is pressed by the superuser or TeamLeader, there is access to this block,
        # which creates a SourcePdfToHandle for the SourcePdf chosen, and assigns it to the company of that user.
        
        if (user_type == "superuser" or user_type == "TeamLeader") and id_assign !="none":
        
            print id_assign
            id_assign = int(id_assign)
        
            source = SourcePdf.objects.filter(pk = id_assign)
        
            user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
            none_user = User.objects.get(username="None")
        
            if len(source):
                        
                source = source[0]                
                tohandle = SourcePdfToHandle(assignedcompany=user_group,assigneduser=none_user,lot_number=-1)
                tohandle.save()
                source.assigndata.add(tohandle)
                source.save()
        
        
        
        #Filters block
     
        if filter_word=="source_assigned":
        
            records_list = SourcePdf.objects.exclude(assigndata=None)
            
        elif filter_word=="source_notassigned":
        
            records_list = SourcePdf.objects.filter(assigndata=None)
            
        else:
            
            filter_word="source_all"
            records_list = SourcePdf.objects.all()

        #Making lists to use in the Search of Coincidences
        
        temp_list = records_list
        final_list = SourcePdf.objects.none()
        
        
        #Check which Search Options are covered
        

        if len(word_job_directory) != 0:
            isJobdirectory = True
            
        else:
            isJobdirectory = False
            
        if len(word_docname) != 0:
            isDocname = True
       
        else:
            isDocname = False
        
        if len(word_doctype) != 0:
            isDoctype = True
       
        else:
            isDoctype = False
        
        if len(word_multipart_filename) != 0:
            isMultipartfilename = True
           
        else:
            isMultipartfilename = False
            
        if len(word_id_docname) != 0:
            isIdDocname = True
       
        else:
            isIdDocname = False
        

        #When at least a word is being searched and there are no Search Options
        
        if word =="all" and isJobdirectory == False and isDocname == False and isDoctype == False and isMultipartfilename == False and isIdDocname == False:
            
            #helper_list = temp_list.filter(ocrrecord_link__Company__icontains=word) | temp_list.filter(ocrrecord_link__Amount__icontains=word)  | temp_list.filter(ocrrecord_link__IssueDate__icontains=word)

            final_list = records_list
                        
            # Unused filters:
            '''no_options_wordlist.filter(sourcedoc_link__filename__icontains=word)| no_options_wordlist.filter(modification_date=word) | no_options_wordlist.filter(record_link__name__icontains=word) | no_options_wordlist.filter(filename__icontains=word) '''

        #When there are Search Options (Amount,etc)
        
        else:
            
            final_list=temp_list
            
            
            if isJobdirectory:
                
                if word_job_directory.startswith('"') and word_job_directory.endswith('"'):
                
                    word_job_directory = word_job_directory.replace('"', '')
                    helper_list = final_list.filter(job_directory__iexact=word_job_directory)
                    word_job_directory = '"'+word_job_directory+'"'
                
                else:
                
                    helper_list = final_list.filter(job_directory__icontains=word_job_directory)
                
                
                final_list = helper_list
                
            
            if isDocname:
                
                if word_docname.startswith('"') and word_docname.endswith('"'):
                
                    word_docname = word_docname.replace('"', '')
                    helper_list = final_list.filter(filename__iexact=word_docname)
                    word_docname = '"'+word_docname+'"'
                    
                else:
                
                    helper_list = final_list.filter(filename__icontains=word_docname)
                
                final_list = helper_list

            if isDoctype:
                
                doctype = SourceDocType.objects.filter(pretty_name__iexact=word_doctype)|SourceDocType.objects.filter(name__iexact=word_doctype.lower())
                doctype = doctype.distinct()
                            
                if len(doctype) == 1:
                
                    helper_list = final_list.filter(modified_document_type = doctype[0])
                    final_list = helper_list
            
            if isMultipartfilename:
                
                if word_multipart_filename.startswith('"') and word_multipart_filename.endswith('"'):
                
                    word_multipart_filename = word_multipart_filename.replace('"', '')
                    helper_list = final_list.filter(multipart_filename__iexact=word_multipart_filename)
                    word_multipart_filename = '"'+word_multipart_filename+'"'
                    
                else:
                
                    helper_list = final_list.filter(multipart_filename__icontains=word_multipart_filename)
                
                final_list = helper_list
            
            if isIdDocname:
        
                separated_string = word_id_docname.split('.', 1)
            
                if len(separated_string) == 2:
                    helper_list = final_list.filter(pk=separated_string[0],filename=separated_string[1])
                    final_list = helper_list
                    
                else:
                    final_list = PdfRecord.objects.none()
        
            
        records_list = final_list   
        
        total_records = records_list.count()
    
        if max_num > total_records:
        
            max_num = total_records
    
            if actual_min_num > max_num and max_num != 0:
            
                actual_min_num = max_num
    
        if records_list:
            
            #Sort by Categories depending on the user's input in the Search Tool:
            
            
            category_fields_order_list = category_fields_order_list.split(',')
            
            category_temp_list = filter(bool, category_fields_order_list)
            
            
            if len(category_temp_list):
            
                for item in category_temp_list:
                    if len(item):
                        
                        records_list = records_list.order_by(item)
            
            
            else:
                records_list = records_list.order_by('pk')
            
            
            category_fields_order_list = ",".join(category_temp_list)
            
            merging_records = records_list
            records_list = records_list[actual_min_num-1:max_num]
    
    elif corpus_word=="corpus_ocr_records":
    
        #Filters block
    
         
        if filter_word=="pdf_error":
        
            records_list = PdfRecord.objects.filter(commentary__contains="Error detected")
            
        elif filter_word=="pdf_linked":
        
            records_list = PdfRecord.objects.filter(status="pdf_linked")
            
        elif filter_word=="pdf_unlinked":
        
            records_list = PdfRecord.objects.filter(status="pdf_unlinked")
        
        else:
            
            filter_word="pdf_all"
            records_list = PdfRecord.objects.all()

        #Making lists to use in the Search of Coincidences
        
        temp_list = records_list
        final_list = PdfRecord.objects.none()
        
        
        #Check which Search Options are covered
        

        if len(word_amount) != 0:
            isAmount = True
            
        else:
            isAmount = False
            

        if len(word_companyname) != 0:
            isCompanyname = True
           
        else:
            isCompanyname = False
            
            
        if len(word_date) != 0:
            isDate = True
            
        else:
            isDate = False
        
        if len(word_doctype) != 0:
            isDoctype = True
       
        else:
            isDoctype = False
        
        if len(word_piecenumber) != 0:
            isPiecenumber = True
       
        else:
            isPiecenumber = False
        
        if len(word_docname) != 0:
            isDocname = True
       
        else:
            isDocname = False
        
        if len(word_id_docname) != 0:
            isIdDocname = True
       
        else:
            isIdDocname = False
        

        #When at least a word is being searched and there are no Search Options
        
        if word =="all" and isAmount == False and isCompanyname == False and isDate == False and isDoctype == False and isPiecenumber == False and isDocname == False and isIdDocname == False:
              
            #helper_list = temp_list.filter(ocrrecord_link__Company__icontains=word) | temp_list.filter(ocrrecord_link__Amount__icontains=word)  | temp_list.filter(ocrrecord_link__IssueDate__icontains=word)

            final_list = records_list
                        
            # Unused filters:
            '''no_options_wordlist.filter(sourcedoc_link__filename__icontains=word)| no_options_wordlist.filter(modification_date=word) | no_options_wordlist.filter(record_link__name__icontains=word) | no_options_wordlist.filter(filename__icontains=word) '''

        #When there are Search Options (Amount,etc)
        
        else:
            
            final_list=temp_list
            
            
            if isAmount:
                
                if word_amount.startswith('"') and word_amount.endswith('"'):
                
                    word_amount = word_amount.replace('"', '')
                    helper_list = final_list.filter(ocrrecord_link__Amount__exact=word_amount)
                    word_amount = '"'+word_amount+'"'
                
                else:
                
                    helper_list = final_list.filter(ocrrecord_link__Amount__icontains=word_amount)
                
                
                final_list = helper_list
                
            
            
            if isCompanyname:
                
                if word_companyname.startswith('"') and word_companyname.endswith('"'):
                
                    word_companyname = word_companyname.replace('"', '')
                    helper_list = final_list.filter(ocrrecord_link__Company__iexact=word_companyname)
                    word_companyname = '"'+word_companyname+'"'
                else:
                
                    helper_list = final_list.filter(ocrrecord_link__Company__icontains=word_companyname)
                
                final_list = helper_list
                
            
            if isDate:
                
                constructed_date = word_date.split("/")
                
                helper_list = final_list

                if len(constructed_date) > 0:
                    day = constructed_date[0]
                    if day != "XX" and day !="NaN" and day != "?":
                        helper_list = helper_list.filter(ocrrecord_link__Day__exact=day)
                    
                if len(constructed_date) > 1:
                    month = constructed_date[1]
                    if month != "XX" and month !="NaN" and month != "?":
                        helper_list = helper_list.filter(ocrrecord_link__Month__exact=month)
                    
                if len(constructed_date) > 2:
                    year = constructed_date[2]
                    if year != "XXXX" and year !="NaN" and year != "?":
                        helper_list = helper_list.filter(ocrrecord_link__Year__exact=year)


                final_list = helper_list
                
                '''helper_list = final_list.filter(ocrrecord_link__IssueDate__icontains=word_date)
                final_list = helper_list'''
            
            if isDoctype:
                
                doctype = SourceDocType.objects.filter(pretty_name__iexact=word_doctype)|SourceDocType.objects.filter(name__iexact=word_doctype.lower())
                doctype = doctype.distinct()
                            
                if len(doctype) == 1:
                
                    helper_list = final_list.filter(modified_document_type = doctype[0])
                    final_list = helper_list
            
            if isPiecenumber:
                
                if word_piecenumber.startswith('"') and word_piecenumber.endswith('"'):
                
                    word_piecenumber = word_piecenumber.replace('"', '')
                    helper_list = final_list.filter(ocrrecord_link__Piece_Number__iexact=word_piecenumber)
                    word_piecenumber = '"'+word_piecenumber+'"'
                else:
                
                    helper_list = final_list.filter(ocrrecord_link__Piece_Number__icontains=word_piecenumber)
                
                
                final_list = helper_list
                
            if isDocname:
                
                if word_docname.startswith('"') and word_docname.endswith('"'):
                
                    word_docname = word_docname.replace('"', '')
                    helper_list = final_list.filter(sourcedoc_link__filename__iexact=word_docname)
                    word_docname = '"'+word_docname+'"'
                    
                else:
                
                    helper_list = final_list.filter(sourcedoc_link__filename__icontains=word_docname)
                
                final_list = helper_list

            if isIdDocname:
        
                separated_string = word_id_docname.split('.', 1)
            
                if len(separated_string) == 2:
                    helper_list = final_list.filter(pk=separated_string[0],sourcedoc_link__filename=separated_string[1])
                    final_list = helper_list
                    
                else:
                    final_list = PdfRecord.objects.none()
        
        
        
        records_list = final_list  

        total_records = records_list.count()
    
        if max_num > total_records:
        
            max_num = total_records
    
            if actual_min_num > max_num and max_num != 0:
            
                actual_min_num = max_num
    
        if records_list:
            
            #Sort by Categories depending on the user's input in the Search Tool:
            
            
            category_fields_order_list = category_fields_order_list.split(',')
            
            category_temp_list = filter(bool, category_fields_order_list)
            
            
            if len(category_temp_list):
            
                for item in category_temp_list:
                    if len(item):
                        
                        records_list = records_list.order_by(item)
            
            
            else:
                records_list = records_list.order_by('pk')
            
            
            category_fields_order_list = ",".join(category_temp_list)
            
            merging_records = records_list
            records_list = records_list[actual_min_num-1:max_num]
                
        
    elif corpus_word=="corpus_internal_records":
    
        
        #Filters block
    
  
        if filter_word=="pdf_error":
        
            records_list = Record.objects.filter(commentary__contains="Error detected")
            
        elif filter_word=="pdf_linked":
        
            records_list = Record.objects.filter(status="linked")
            
        elif filter_word=="pdf_unlinked":
        
            records_list = Record.objects.filter(status="unlinked")
        
        else:
            
            filter_word="pdf_all"
            records_list = Record.objects.all()

        #Making lists to use in the Search of Coincidences
        
        temp_list = records_list
        final_list = Record.objects.none()
        
        
        #Check which Search Options are covered
        
        if len(word_amount_credit) != 0:
            isAmountcredit = True
            
        else:
            isAmountcredit = False
        
        if len(word_amount_debit) != 0:
            isAmountdebit = True
            
        else:
            isAmountdebit = False

        if len(word_companyname) != 0:
            isCompanyname = True
           
        else:
            isCompanyname = False
            
            
        if len(word_date) != 0:
            isDate = True
            
        else:
            isDate = False
        

        if len(word_piecenumber) != 0:
            isPiecenumber = True
       
        else:
            isPiecenumber = False
            
        if len(word_accountnumber) != 0:
            isAccountnumber = True
       
        else:
            isAccountnumber = False
            
        if len(word_movnumber) != 0:
            isMovementnumber = True
       
        else:
            isMovementnumber = False
            
        if len(word_journal) != 0:
            isJournal = True
       
        else:
            isJournal = False
            
        if len(word_s) != 0:
            isS = True
       
        else:
            isS = False
            
        if len(word_lett) != 0:
            isLett = True
       
        else:
            isLett = False
            
        if len(word_docname) != 0:
            isDocname = True
       
        else:
            isDocname = False
        
        if len(word_id) != 0:
            isId = True
       
        else:
            isId = False
        

        #When at least a word is being searched and there are no Search Options
        
        if word =="all" and isAmountcredit == False and isAmountdebit == False and isCompanyname == False and isDate == False and isPiecenumber == False and isAccountnumber == False and isMovementnumber == False and isJournal == False and isS == False and isLett == False and isId == False:
              
            #helper_list = temp_list.filter(ocrrecord_link__Company__icontains=word) | temp_list.filter(ocrrecord_link__Amount__icontains=word)  | temp_list.filter(ocrrecord_link__IssueDate__icontains=word)

            final_list = records_list
                        
            # Unused filters:
            '''no_options_wordlist.filter(sourcedoc_link__filename__icontains=word)| no_options_wordlist.filter(modification_date=word) | no_options_wordlist.filter(record_link__name__icontains=word) | no_options_wordlist.filter(filename__icontains=word) '''

        #When there are Search Options (Amount,etc)
        
        else:
            
            final_list=temp_list
            
            
            if isAmountcredit:
                
                if word_amount_credit.startswith('"') and word_amount_credit.endswith('"'):
                
                    word_amount_credit = word_amount_credit.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__Credit__exact=word_amount_credit)
                    word_amount_credit = '"'+word_amount_credit+'"'
                
                else:
                
                    helper_list = final_list.filter(internalrecord_link__Credit__icontains=word_amount_credit)
                
                
                final_list = helper_list
                
            if isAmountdebit:
                
                if word_amount_debit.startswith('"') and word_amount_debit.endswith('"'):
                
                    word_amount_debit = word_amount_debit.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__Debit__exact=word_amount_debit)
                    word_amount_debit = '"'+word_amount_debit+'"'
                
                else:
                
                    helper_list = final_list.filter(internalrecord_link__Debit__icontains=word_amount_debit)
                
                
                final_list = helper_list
            
            if isCompanyname:
                
                if word_companyname.startswith('"') and word_companyname.endswith('"'):
                
                    word_companyname = word_companyname.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__Company__iexact=word_companyname)
                    word_companyname = '"'+word_companyname+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__Company__icontains=word_companyname)
                
                final_list = helper_list
                
            
            if isDate:
                
                constructed_date = word_date.split("/")
                
                helper_list = final_list

                if len(constructed_date) > 0:
                    day = constructed_date[0]
                    if day != "XX" and day !="NaN" and day != "?":
                        helper_list = helper_list.filter(internalrecord_link__Day__exact=day)
                    
                if len(constructed_date) > 1:
                    month = constructed_date[1]
                    if month != "XX" and month !="NaN" and month != "?":
                        helper_list = helper_list.filter(internalrecord_link__Month__exact=month)
                    
                if len(constructed_date) > 2:
                    year = constructed_date[2]
                    if year != "XXXX" and year !="NaN" and year != "?":
                        helper_list = helper_list.filter(internalrecord_link__Year__exact=year)


                final_list = helper_list
            
            
            if isPiecenumber:
                
                if word_piecenumber.startswith('"') and word_piecenumber.endswith('"'):
                
                    word_piecenumber = word_piecenumber.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__NoPiece__iexact=word_piecenumber)
                    word_piecenumber = '"'+word_piecenumber+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__NoPiece__icontains=word_piecenumber)
                
                
                final_list = helper_list
                
            if isAccountnumber:
                
                if word_accountnumber.startswith('"') and word_accountnumber.endswith('"'):
                
                    word_accountnumber = word_accountnumber.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__AccountNum__iexact=word_accountnumber)
                    word_accountnumber = '"'+word_accountnumber+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__AccountNum__icontains=word_accountnumber)
                
                
                final_list = helper_list
                
            if isMovementnumber:
                
                if word_movnumber.startswith('"') and word_movnumber.endswith('"'):
                
                    word_movnumber = word_movnumber.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__NoMvt__iexact=word_movnumber)
                    word_movnumber = '"'+word_movnumber+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__NoMvt__icontains=word_movnumber)
                
                
                final_list = helper_list
                
            if isJournal:
                
                if word_journal.startswith('"') and word_journal.endswith('"'):
                
                    word_journal = word_journal.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__Journal__iexact=word_journal)
                    word_journal = '"'+word_journal+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__Journal__icontains=word_journal)
                
                
                final_list = helper_list

            if isS:
                
                if word_s.startswith('"') and word_s.endswith('"'):
                
                    word_s = word_s.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__S__iexact=word_s)
                    word_s = '"'+word_s+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__S__icontains=word_s)
                
                
                final_list = helper_list
                
            if isLett:
                
                if word_lett.startswith('"') and word_lett.endswith('"'):
                
                    word_lett = word_lett.replace('"', '')
                    helper_list = final_list.filter(internalrecord_link__Lett__iexact=word_lett)
                    word_lett = '"'+word_lett+'"'
                else:
                
                    helper_list = final_list.filter(internalrecord_link__Lett__icontains=word_lett)
                
                
                final_list = helper_list
                
            if isId:
        

                if len(word_id) > 0:
                    helper_list = final_list.filter(pk=word_id)
                    final_list = helper_list
                    
                else:
                    final_list = PdfRecord.objects.none()
     
    
        records_list = final_list   
        
        total_records = records_list.count()
    
        if max_num > total_records:
        
            max_num = total_records
    
            if actual_min_num > max_num and max_num != 0:
            
                actual_min_num = max_num
    
        if records_list:
            
            #Sort by Categories depending on the user's input in the Search Tool:
            
            
            category_fields_order_list = category_fields_order_list.split(',')
            
            category_temp_list = filter(bool, category_fields_order_list)
            
            
            if len(category_temp_list):
            
                for item in category_temp_list:
                    if len(item):
                        
                        records_list = records_list.order_by(item)
            
            
            else:
                records_list = records_list.order_by('pk')
            
            
            category_fields_order_list = ",".join(category_temp_list)
            
            
            merging_records = records_list
            records_list = records_list[actual_min_num-1:max_num]
    
    ##### COMMON BLOCK ####
    
    
    
    try:
        export_mark = request.POST['export_mark']
    except (KeyError):
        
        export_mark = "none"
    
    #if export_mark == "export_mark":
    
    
    if export_mark == "export_mark" and corpus_word!="corpus_internal_records":
    
        if len(merging_records) > 10:
        
            merging_records = merging_records[:10]
 
        print len(merging_records)

        response = HttpResponse(mimetype="application/pdf")
        response['Content-Disposition'] = 'attachment; filename=output_document.pdf'
        output = PdfFileWriter()
        
        with transaction.commit_on_success():
            for record in merging_records:
            
                if corpus_word=="corpus_source_records":
                    
                    source_url = "http://54.200.180.182/sourcepdfs/%s/%s" %(record.job_directory, record.filename)
                   
                if corpus_word=="corpus_ocr_records":
                    
                    source_url = "http://54.200.180.182/sourcepdfs/%s/%s" %(record.sourcedoc_link.job_directory, record.sourcedoc_link.filename)

                remoteFile = urlopen(Request(source_url)).read()
                memoryFile = StringIO(remoteFile)
                input_pdf = PdfFileReader(memoryFile)
                
                output.addPage(input_pdf.getPage(0))
            
            
            outputStream = StringIO()
            output.write(outputStream)
            response.write(outputStream.getvalue())
            return response
        
        
    showing_records = records_list.count()
    

    page_counter_end = actual_min_num + showing_records - 1
    
    plus_limit = total_records-50
    
    if showing_records == 0:
    
        actual_min_num = 0
        max_num = 0  
        page_counter_end = 0
     
    
    
    context = {'user_type':user_type,
    'records_list':records_list,'types_list':types_list,'companyname_list':companyname_list,'corpus_word':corpus_word,'filter_word': filter_word,
    'word_amount':word_amount,'word_companyname':word_companyname,'word_amount_credit':word_amount_credit,'word_amount_debit':word_amount_debit,
    'word_date':word_date,'word_doctype':word_doctype,'word_piecenumber':word_piecenumber,'word_accountnumber':word_accountnumber,
    'word_movnumber':word_movnumber,'word_journal':word_journal,'word_s':word_s,'word_lett':word_lett,'word_id':word_id,
    'word_job_directory':word_job_directory,'word_multipart_filename':word_multipart_filename,
    'word_docname':word_docname,'word_id_docname':word_id_docname,'total_records':total_records,
    'page_counter_beginning':actual_min_num,'page_counter_end':page_counter_end,'plus_limit':plus_limit,
    'category_fields_order_list':category_fields_order_list,'the_user':the_user}
    
    return render(request,'enersectapp/search_tool.html',context)