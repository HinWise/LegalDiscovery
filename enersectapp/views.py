from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate

from django.shortcuts import get_object_or_404, render, redirect,render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template import RequestContext
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime
from django.db import transaction
from django.db import connection
import re
import json,csv
from django.core import serializers
import random


from enersectapp.models import Record,UserInterfaceType,PdfRecord,SourceDocType,FilterSearchWords,InternalRecord,OcrRecord,SourcePdf,CompanyOriginal,CompanyTemplate,SourcePdfToHandle,UserProfile


def maintenance_screen(request):
  
    return render(request,'enersectapp/maintenance_screen.html',context)

def app_login(request):
  
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                #return HttpResponseRedirect('enersectapp:main')
                return HttpResponseRedirect(reverse('enersectapp:main', args=()))
                #return reverse('enersectapp:main', args=())
    return render_to_response('enersectapp/app_login.html', context_instance=RequestContext(request))

def main_menu(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    interface_type_list = UserInterfaceType.objects.all()
    the_user = request.user
   
    context = {'uitype_list':interface_type_list,"the_user":the_user}
    return render(request,'enersectapp/app_index.html',context)

     
def linkui(request):
    latest_uitype_list = UserInterfaceType.objects.all()
    context = {'latest_uitype_list':latest_uitype_list}
    return render(request,'enersectapp/linkui_spiderweb.html',context)

 
def linkui_spiderweb(request):
    
    '''if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))'''
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = FilterSearchWords.objects.get(pk=1) 
    #word = p.pdf_searchword
    word="all"
    word_amount= ""
    word_companyname=""
    word_date=""
    word_docname=""
    filterword = p.pdf_filterword
    pdf_records_list=[]
    search_options = ""
    
    '''try:
        word = request.POST['search_word']
    except (KeyError):
        
        word = p.pdf_searchword'''
        
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
        word_docname = request.POST['search_word_docname']
    except (KeyError):
        
        word_docname=""
    
    try:
        filterword = request.POST['filter_word']
    except (KeyError):
        
        filterword = p.pdf_filterword
    
    #word = str(word)
    word_amount= str(word_amount).encode("utf8")
    word_companyname= word_companyname.encode("utf8")
    word_date= str(word_date).encode("utf8")
    word_docname= str(word_docname).encode("utf8")
    filterword = filterword.lower()    
    
    #p.pdf_searchword = word 
    p.pdf_filterword = filterword
    p.save()    
        
    #Filters block
    
    if filterword=="pdf_all":
    
        pdf_records_list = PdfRecord.objects.all()
        
    elif filterword=="pdf_error":
    
        pdf_records_list = PdfRecord.objects.filter(commentary__contains="Error detected")
        
    elif filterword=="pdf_linked":
    
        pdf_records_list = PdfRecord.objects.filter(status="pdf_linked")
        
    elif filterword=="pdf_unlinked":
    
        pdf_records_list = PdfRecord.objects.filter(status="pdf_unlinked")
        
       
    #Making lists to use in the Search of Coincidences
    
    temp_list = pdf_records_list
    final_list = pdf_records_list.filter(status__exact="Test")
    
    
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
      
        
    if len(word_docname) != 0:
        isDocname = True
   
    else:
        isDocname = False
       
    
    #When at least a word is being searched and there are no Search Options
    
    if word =="all" and isAmount == False and isCompanyname == False and isDate == False and isDocname == False:
          
        #helper_list = temp_list.filter(ocrrecord_link__Company__icontains=word) | temp_list.filter(ocrrecord_link__Amount__icontains=word)  | temp_list.filter(ocrrecord_link__IssueDate__icontains=word)

        final_list = pdf_records_list
                    
        # Unused filters:
        '''no_options_wordlist.filter(sourcedoc_link__filename__icontains=word)| no_options_wordlist.filter(modification_date=word) | no_options_wordlist.filter(record_link__name__icontains=word) | no_options_wordlist.filter(filename__icontains=word) '''
    

    #When there are Search Options (Amount,etc)
    
    else:
        
        final_list=temp_list
        
        
        if isAmount:
              
            
            helper_list = final_list.filter(ocrrecord_link__Amount__icontains=word_amount)
            
            final_list = helper_list
            
        
        
        if isCompanyname:
                     
            helper_list = final_list.filter(ocrrecord_link__Company__icontains=word_companyname)
            final_list = helper_list
            
        
        if isDate:
                
            helper_list = final_list.filter(ocrrecord_link__IssueDate__icontains=word_date)
            final_list = helper_list
            
            
        if isDocname:
                    
            helper_list = final_list.filter(sourcedoc_link__filename__icontains=word_docname)
            final_list = helper_list
                 
    
    
    actual_min_num = 0
    
    try:
        prev_next_results = request.POST['prev_next_results']
        prev_next_results = str(prev_next_results)
    except (KeyError):
        
        prev_next_results = ""
        
    try:
        actual_min_num = request.POST['actual_min_num']
        actual_min_num = int(actual_min_num)
    except (KeyError):
        
        actual_min_num = 0
    
    
    if(prev_next_results == ""):
        actual_min_num = 0
    
    if(prev_next_results == "Prev"):
        actual_min_num -= 10
        
    if(prev_next_results == "Next"):
        actual_min_num += 10
    
    max_num = actual_min_num + 10
    
    pdf_records_list = final_list       
    
    total_pdf_records = pdf_records_list.count()
    

    pdf_records_list = pdf_records_list.order_by('commentary').order_by('-status')[actual_min_num:max_num]

    showing_records = pdf_records_list.count()
    
    page_counter_end = actual_min_num+showing_records
    
    plus_limit = total_pdf_records-10
     
    next_unlinked_record = Record.objects.filter(status="unlinked").exclude(skip_counter=1).exclude(name="ControlRecord").order_by('skip_counter')[:1]
    unlinked_records_remaining = Record.objects.filter(status="unlinked").exclude(skip_counter=1).exclude(name="ControlRecord").count()
    context = {'next_unlinked_record':next_unlinked_record,'unlinked_records_remaining':unlinked_records_remaining,
    'pdf_records_list':pdf_records_list,'searchword_filterword': p,'word_amount':word_amount,'word_companyname':word_companyname,
    'word_date':word_date,'word_docname':word_docname,'total_pdf_records':total_pdf_records,
    'page_counter_beginning':actual_min_num,'page_counter_end':page_counter_end,'plus_limit':plus_limit}
    return render(request,'enersectapp/linkui_spiderweb.html',context)
    
def linkui_link(request, pdfrecord_id, record_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = get_object_or_404(PdfRecord, pk=pdfrecord_id)
    r = get_object_or_404(Record, pk=record_id)
    
    p.status = "pdf_linked"
    p.linked_style_class = 'ui-state-custom-linked'
    r.linked_style_class = 'ui-state-custom-linked'
    p.record_link = r
    p.save()
    r.status = "linked"
    r.save()
    
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb', args=()))


def linkui_unlink(request, pdfrecord_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = get_object_or_404(PdfRecord, pk=pdfrecord_id)
    r = p.record_link
    q = get_object_or_404(Record, name="ControlRecord")
    
    p.status = "pdf_unlinked"
    p.linked_style_class = 'nolink'
    r.linked_style_class = 'nolink'
    p.record_link = q
    p.save()
    r.status = "unlinked"
    r.save()
        
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb', args=()))    
    
def linkui_flag(request):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        pdfrecord_id = request.POST['flag_form_record_id']
    except (KeyError):
        
        pdfrecord_id=""
        
    try:
        error_category = request.POST['flag_form_category']
    except (KeyError):
        
        error_category=""
        
    try:
        text_content = request.POST['flag_form_text']
    except (KeyError):
        
        text_content=""
    
    
    p = get_object_or_404(PdfRecord, pk=pdfrecord_id)
    
    p.error_style_class = 'ui-state-custom-error'
    p.commentary = 'Error detected: '+error_category+'; '+text_content
 
    p.save()
 
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb', args=()))    
    
def linkui_unflag(request, pdfrecord_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = get_object_or_404(PdfRecord, pk=pdfrecord_id)
        
    p.error_style_class = 'noerror'
    p.commentary = 'Error solved'
 
    p.save()
        
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb', args=()))          


def linkui_skip(request, record_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    r = get_object_or_404(Record, pk=record_id)
   
    #num = int(r.skip_counter)+1
    num = 1
   
    r.skip_counter = num
    r.save()
    
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb', args=()))

#####---Starts the Linkui view for "Viceversa", when an unlinked Pdf Record is called and multiple Records
# are dynamic

def linkui_spiderweb_viceversa(request):
    
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = FilterSearchWords.objects.get(pk=1) 
    #word = p.pdf_searchword
    word="all"
    word_amount= ""
    word_companyname=""
    word_date=""
    word_piecenum=""
    filterword = p.pdf_filterword
    records_list=[]
    search_options = ""
    
    '''try:
        word = request.POST['search_word']
    except (KeyError):
        
        word = p.pdf_searchword'''
        
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
        word_piecenum = request.POST['search_word_piecenum']
    except (KeyError):
        
        word_piecenum=""
    
    try:
        filterword = request.POST['filter_word']
    except (KeyError):
        
        filterword = p.pdf_filterword
    
    #word = str(word)
    word_amount= str(word_amount).encode("utf8")
    word_companyname= word_companyname.encode("utf8")
    word_date= str(word_date).encode("utf8")
    word_piecenum= str(word_piecenum).encode("utf8")
    filterword = filterword.lower()    
    
    #p.pdf_searchword = word 
    p.pdf_filterword = filterword
    p.save()    
        
    #Filters block
    
    if filterword=="pdf_all":
    
        records_list = Record.objects.all()
        
    elif filterword=="pdf_error":
    
        records_list = Record.objects.filter(commentary__icontains="Error detected")
        
    elif filterword=="pdf_linked":
    
        records_list = Record.objects.filter(status="linked")
        
    elif filterword=="pdf_unlinked":
    
        records_list = Record.objects.filter(status="unlinked")
        
       
    #Making lists to use in the Search of Coincidences
    
    temp_list = records_list
    final_list = records_list.filter(status__exact="Test")
    
    
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
      
        
    if len(word_piecenum) != 0:
        isPieceNum = True
   
    else:
        isPieceNum = False
       
    
    #When at least a word is being searched and there are no Search Options
    
    if word =="all" and isAmount == False and isCompanyname == False and isDate == False and isPieceNum == False:
          
        #helper_list = temp_list.filter(ocrrecord_link__Company__icontains=word) | temp_list.filter(ocrrecord_link__Amount__icontains=word)  | temp_list.filter(ocrrecord_link__IssueDate__icontains=word)

        final_list = records_list
                    
        # Unused filters:
        '''no_options_wordlist.filter(sourcedoc_link__filename__icontains=word)| no_options_wordlist.filter(modification_date=word) | no_options_wordlist.filter(record_link__name__icontains=word) | no_options_wordlist.filter(filename__icontains=word) '''
    

    #When there are Search Options (Amount,etc)
    
    else:
        
        final_list=temp_list
        
        
        if isAmount:
                
            
            helper_list = final_list.filter(internalrecord_link__Credit__icontains=word_amount)|final_list.filter(internalrecord_link__Debit__icontains=word_amount)
            
            final_list = helper_list.distinct()
            
        
        
        if isCompanyname:
                     
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
            
            
        if isPieceNum:
                   
            helper_list = final_list.filter(internalrecord_link__NoPiece__exact=word_piecenum)
            final_list = helper_list
                 
    
    
    actual_min_num = 0
    
    try:
        prev_next_results = request.POST['prev_next_results']
        prev_next_results = str(prev_next_results)
    except (KeyError):
        
        prev_next_results = ""
        
    try:
        actual_min_num = request.POST['actual_min_num']
        actual_min_num = int(actual_min_num)
    except (KeyError):
        
        actual_min_num = 0
    
    
    if(prev_next_results == ""):
        actual_min_num = 0
    
    if(prev_next_results == "Prev"):
        actual_min_num -= 10
        
    if(prev_next_results == "Next"):
        actual_min_num += 10
    
    max_num = actual_min_num + 10
    
    records_list = final_list       
    
    total_records = records_list.count()
    

    records_list = records_list.order_by('commentary').order_by('-status')[actual_min_num:max_num]

    showing_records = records_list.count()
    
    page_counter_end = actual_min_num+showing_records
    
    plus_limit = total_records-10
     
    next_unlinked_pdf_record = PdfRecord.objects.filter(status="pdf_unlinked").exclude(skip_counter=1).exclude(name="ControlRecord").order_by('skip_counter')[:1]
    unlinked_pdf_records_remaining = PdfRecord.objects.filter(status="pdf_unlinked").exclude(skip_counter=1).exclude(name="ControlRecord").count()
    context = {'next_unlinked_pdf_record':next_unlinked_pdf_record,'unlinked_pdf_records_remaining':unlinked_pdf_records_remaining,
    'records_list':records_list,'searchword_filterword': p,'word_amount':word_amount,'word_companyname':word_companyname,
    'word_date':word_date,'word_piecenum':word_piecenum,'total_records':total_records,
    'page_counter_beginning':actual_min_num,'page_counter_end':page_counter_end,'plus_limit':plus_limit}
    return render(request,'enersectapp/linkui_spiderweb_viceversa.html',context)
    
def linkui_link_viceversa(request, pdfrecord_id, record_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = get_object_or_404(PdfRecord, pk=pdfrecord_id)
    r = get_object_or_404(Record, pk=record_id)
    
    p.status = "pdf_linked"
    p.linked_style_class = 'ui-state-custom-linked'
    r.linked_style_class = 'ui-state-custom-linked'
    p.record_link = r
    p.save()
    r.status = "linked"
    r.save()
    
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb_viceversa', args=()))


def linkui_unlink_viceversa(request, record_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))

    r = get_object_or_404(Record, pk=record_id)
    p = PdfRecord.objects.filter(record_link=r)[0]
    q = get_object_or_404(Record, name="ControlRecord")
    
    p.status = "pdf_unlinked"
    p.linked_style_class = 'nolink'
    r.linked_style_class = 'nolink'
    p.record_link = q
    p.save()
    r.status = "unlinked"
    r.save()
        
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb_viceversa', args=()))    
    
def linkui_flag_viceversa(request):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        record_id = request.POST['flag_form_record_id']
    except (KeyError):
        
        record_id=""
        
    try:
        error_category = request.POST['flag_form_category']
    except (KeyError):
        
        error_category=""
        
    try:
        text_content = request.POST['flag_form_text']
    except (KeyError):
        
        text_content=""
    
    
    p = get_object_or_404(Record, pk=record_id)
    
    p.error_style_class = 'ui-state-custom-error'
    p.commentary = 'Error detected: '+error_category+'; '+text_content
 
    p.save()
 
    
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb_viceversa', args=()))    
    
def linkui_unflag_viceversa(request, record_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    p = get_object_or_404(Record, pk=record_id)
        
    p.error_style_class = 'noerror'
    p.commentary = 'Error solved'
 
    p.save()
        
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb_viceversa', args=()))          


def linkui_skip_viceversa(request, pdfrecord_id):
    
    the_user = request.user
    
    is_superuser = the_user.is_superuser
    is_teamleader = False
    
    if len(the_user.groups.filter(name="TeamLeaders"))>0:
        is_teamleader = True

    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    if is_superuser == False and is_teamleader == False:
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    r = get_object_or_404(PdfRecord, pk=pdfrecord_id)
   
    #num = int(r.skip_counter)+1
    num = 1
   
    r.skip_counter = num
    r.save()
    
    return HttpResponseRedirect(reverse('enersectapp:linkui_spiderweb_viceversa', args=()))    


def dataentryui_spider(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    #Mode indicates if the Pdfs to categorize are taken from the "No Category" Pool on the Source Pdfs, the "Other" Pool on the Entries, or All Entries.
    
    try:
        document_type = request.POST['doctype']
        
    except (KeyError):
    
        document_type='Document Type'
        
        
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="Arabic")[0]
    
    if(the_user.username=="dimaelkezee"):
        document_type = 'Arabic'
    
    sourcepdfs_list = SourcePdf.objects.all()
    count_assigned = 0
    count_done = 0
    
    if(the_user.is_superuser == True):
    
        sourcepdfs_handles_list = SourcePdfToHandle.objects.filter(assignedcompany=user_group).exclude(checked="checked")[:1]
        
        if sourcepdfs_handles_list:
            
            sourcepdfs_handle_item = sourcepdfs_handles_list[0]
            sourcepdfs_list = SourcePdf.objects.filter(assigndata=sourcepdfs_handle_item)[0]
            
        else:
            print "NO SOURCEPDF HANDLE MATCHING THE QUERY SUPERUSER!"+the_user.username
            
            sourcepdfs_list = SourcePdf.objects.none()
        
        
        
        #Making it this way makes it 400 ms faster, but it is more confusing and less robust
        #Commented way is the old way
        
        #sourcepdfs_list = SourcePdf.objects.filter(assigndata__assignedcompany=user_group)
        #sourcepdfs_list = sourcepdfs_list.exclude(assigndata__checked="checked")[0]

        
    elif len(the_user.groups.filter(name="TeamLeaders"))==0:
        
        sourcepdfs_list = sourcepdfs_list.filter(assigndata__assignedcompany=user_group,assigndata__assigneduser=the_user)
        
        #sourcepdfs_list = sourcepdfs_list.filter(assigndata__assigneduser=the_user)
        

        count_assigned = sourcepdfs_list.count()

        count_done = sourcepdfs_list.filter(assigndata__checked="checked",assigndata__assigneduser=the_user).count()
        
        sourcepdfs_handles_list = SourcePdfToHandle.objects.filter(assigneduser=the_user).exclude(checked="checked")[:1]
        
        if sourcepdfs_handles_list:
            sourcepdfs_handle_item = sourcepdfs_handles_list[0]
            sourcepdfs_list = SourcePdf.objects.filter(assigndata=sourcepdfs_handle_item)[0]
        else:
            #print "NO SOURCEPDF HANDLE MATCHING THE QUERY! BY USER"+the_user.username
            sourcepdfs_list = SourcePdf.objects.none()
        
        #Read the comment above, in the superuser. This is for the same reasons
        #Commented is the old way
        #sourcepdfs_list = sourcepdfs_list.filter(assigndata__checked="unchecked",assigndata__assigneduser=the_user)| sourcepdfs_list.filter(assigndata__checked="error",assigndata__assigneduser=the_user)[:1]

        
 
    
    else:
        #Uncomment this to produce an Error 500 when entering the Data Entry Tool as a Team Leader
        #print "Team Leaders"
        #sourcepdfs_list = []
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
  
    
    
    companyname_list = CompanyTemplate.objects.all().order_by('companyname_base').values_list('companyname_base',flat=True).distinct()
    
    
    #return response

    context = {'document_type':document_type,'companyname_list':companyname_list,
    'sourcepdfs_list':sourcepdfs_list,'the_user':the_user.username,'user_group':user_group.name,
    'count_assigned':count_assigned,'count_done':count_done}
    return render(request,'enersectapp/dataentryui_spider.html',context)
    
'''def link(request, pdfrecord_id, record_id):
    return HttpResponse("You're linking %s and %s." % (pdfrecord_id,record_id))'''

def dataentryui_savedata(request):

    try:
        doctype = request.POST['doctype']
    except:
        doctype = "NoDocTypeField"
   
    try:
        currency = request.POST['currency']
    except:
        currency = "NoCurrencyField"
    
    try:
        amount = request.POST['amount']
    except:
        amount = "NoAmountField"
    
    try:
        company_name = request.POST['company_name']
    except:
        company_name = "NoCompanyNameField"
        
    try:
        company_address = request.POST['company_address']
    except:
        company_address = "NoCompanyAddressField"
        
    try:
        company_telephone = request.POST['company_telephone']
    except:
        company_telephone = "NoCompanyTelephoneField"
        
    try:
        company_city = request.POST['company_city']
    except:
        company_city = "NoCompanyCityField"
        
    try:
        company_country = request.POST['company_country']
    except:
        company_country = "NoCompanyCountryField"
        
    try:
        company_template = request.POST['company_template']
    except:
        company_template = "NoCompanyTemplateField"
    
    try:
        issuedate = request.POST['issuedate']
    except:
        issuedate = "NoIssueDateField"
        
    try:
        issuedate_day = request.POST['issuedate_day']
    except:
        issuedate_day = "NoIssueDateDayField"
    
    if issuedate_day == "NaN":
        issuedate_day = "MISSING"
    
    try:
        issuedate_month = request.POST['issuedate_month']
    except:
        issuedate_month = "NoIssueDateMonthField"
    
    if issuedate_month == "NaN":
        issuedate_month = "MISSING"
    
    try:
        issuedate_year = request.POST['issuedate_year']
    except:
        issuedate_year = "NoIssueDateYearField"
    
    if issuedate_year == "NaN":
        issuedate_year = "MISSING"
    
    try:
        docnumber = request.POST['docnumber']
    except:
        docnumber = "NoDocNumberField"
    
    try:
        memo = request.POST['memo']
    except:
        memo = "NoMemoField"
        
    try:
        translation_memo = request.POST['translation_memo']
    except:
        translation_memo = "NoTranslationField"
        
    try:
        arabic = request.POST['arabic']
    except:
        arabic = "NoArabicField"

    try:
        sourcedoc = request.POST['sourcedoc']
    except:
        sourcedoc = "NoSourceDocField"
        
    try:
        file_name = request.POST['save_filename']
    except:
        file_name = "NoFilenameField"
        
    try:
        purch_order_num = request.POST['purchasenumber']
    except:
        purch_order_num = "NoPurchaseOrderNumberField"
        
    try:
        piece_number = request.POST['piecenumber']
    except:
        piece_number = "NoPieceNumberField"
    
    try:
        page_number = request.POST['pagenumber']
    except:
        page_number = "NoPageNumberField"
    
    try:
        accountnum = request.POST['accountnum']
    except:
        accountnum = "NoAccountNumberField"
        

    control_rec = Record.objects.get(name="ControlRecord")
    
    if(doctype!="NoDocTypeField"):
    
        doctype = doctype.lower()
        
        if doctype == "invoice/facture":
            doctype = "invoice"
            
        if doctype == "receipt/recu":
            doctype = "receipt"
            
        if doctype == "contract page 1":
            doctype = "contract page 1"
            
        if doctype == "contract page X":
            doctype = "contract page X"
        
        if doctype == "purchase order/bon de commande":
            doctype = "purchase order"
        
        if doctype == "arabic":
            
            translation_type = "arabic translation"
            

            
    doctype_class = SourceDocType.objects.get(name=doctype)
    
    
    if(doctype == "blank"):
        
        new_ocr = OcrRecord(Amount="Blank",Currency="Blank",Company="Blank",Address="Blank",City="Blank",Country="Blank",Telephone="Blank",Source_Bank_Account="Blank",Document_Type="Blank",IssueDate="Blank",Day="Blank",Month="Blank",Year="Blank",ContainsArabic="Blank",Blank="Blank",Notes="Blank",Unreadable="Blank",Document_Number="Blank",PurchaseOrder_Number="Blank",Piece_Number="Blank",Page_Number="Blank",Translation_Notes = "Blank")
        company_link = CompanyTemplate.objects.get(companyname_base="ControlCompanyTemplate")
    
    else:
        new_ocr = OcrRecord(Amount=amount,Currency=currency,Company=company_name,Address=company_address,City=company_city,Country=company_country,Telephone=company_telephone,Source_Bank_Account=accountnum,Document_Type=doctype,IssueDate=issuedate,Day=issuedate_day,Month=issuedate_month,Year=issuedate_year,ContainsArabic=arabic,Blank="none",Document_Number=docnumber,Notes=memo,Unreadable="no",PurchaseOrder_Number=purch_order_num,Piece_Number=piece_number,Page_Number=page_number,Translation_Notes = translation_memo)
        
    
    try:
        company_link = CompanyTemplate.objects.filter(companyname_base=company_template)[0]

    except:
        company_link = ""
        
        comp_origin = CompanyOriginal.objects.get(companyname_original="ControlCompanyOriginal")
        company_link = CompanyTemplate(companyname_base=company_name,companyaddress_base=company_address,companytelephone_base=company_telephone ,companycity_base=company_city,companycountry_base=company_country,company_original=comp_origin)
        company_link.save()
           
    
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="Arabic")[0]
    
    new_ocr.OcrAuthor = the_user
    new_ocr.OcrByCompany = user_group
    new_ocr.OcrCreationDate = datetime.datetime.now().strftime("%d/%m/%Y")
    
    
    source = SourcePdf.objects.get(filename=file_name)
   
    
    handle = ""
    
    if(the_user.is_superuser == True):
        handle = source.assigndata.get(assigneduser=the_user)
        handle.checked = "checked"
        handle.times_checked = int(handle.times_checked) + 1
        
    else:
        handle = source.assigndata.get(assigneduser=the_user)
        handle.checked = "checked"
        handle.times_checked = int(handle.times_checked) + 1
    
    handle.save()
    source.save()
    

    new_ocr.save()
    
    #If it is duplicated (Was entered before), mark previous Entries as "Revised"
    
    is_duplicated_list = PdfRecord.objects.filter(sourcedoc_link = source,ocrrecord_link__OcrByCompany = user_group)
    
    if is_duplicated_list.count() > 0:
        
        for item in is_duplicated_list:
            item.audit_mark = "duplicatemarked_reentered"
            item.save()
    
    translation_type = "no"

    
    if not doctype_class:
        print "ATTENTION!DOC TYPE CLASS NOT SELECTED, views.py Line 1181!"
    
    new_pdf = PdfRecord(modified_doctype_from=doctype,original_document_type=doctype_class,modified_document_type=doctype_class,record_link=control_rec,ocrrecord_link=new_ocr,sourcedoc_link=source,companytemplate_link=company_link,commentary="No modifications",skip_counter='0',audit_mark="None",modification_date=datetime.datetime.now().replace(tzinfo=timezone.utc),modification_author=the_user.username,translated=translation_type)
    
    new_pdf.save()
    
    #Arabic special case, saving the translation in the user that made it
    
    if doctype == "arabic":
            
            user_profile = UserProfile.objects.get(user=the_user)
            
            if len(user_profile.modifiedpdfs_translated_arabic.filter(pk=new_pdf.pk))==0:
                user_profile.modifiedpdfs_translated_arabic.add(new_pdf)
                user_profile.save()
    
    
    return HttpResponseRedirect(reverse('enersectapp:dataentryui_spider', args=()))

def sudo_assignsourcepdfsui(request):
        
        
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        sourcepdf_list = request.POST['sourcepdfs_list']
        
    except (KeyError):
    
        sourcepdf_list ='SourcePdf List Empty'
    
    try:
        the_user_name = request.POST['the_user']
        
    except (KeyError):
    
        the_user_name ='User Name Empty'
        
    try:
        user_group_name = request.POST['user_group']
        
    except (KeyError):
    
        user_group_name ='User Group Name Empty'
          
    try:
        company_name = request.POST['company_name']
        
    except (KeyError):
    
        company_name ='Company To Assign Empty'
    
    #print sourcepdf_list,the_user,company_name,user_group
    
    sourcepdf_list = str(sourcepdf_list)
    sourcepdf_list = sourcepdf_list.split('|');
    sourcepdf_list = sourcepdf_list[:-1]
    
    controluser = User.objects.get(username="None")
    assigned_group = Group.objects.get(name=company_name)
    
    with transaction.commit_on_success():
        for item in sourcepdf_list:
            if item:
                #the_user.assignedsourcepdfs.add(source)
                
                source = SourcePdf.objects.get(id=int(item))
                
                if source.assigndata.exclude(assignedcompany__name=company_name):
                    tohandle = SourcePdfToHandle(assignedcompany=assigned_group,assigneduser=controluser)
                    tohandle.save()
                    source.assigndata.add(tohandle)
                    source.save()
                    #the_user.save()
                
    return redirect('/admin/enersectapp/sourcepdf')
    
def lead_assignsourcepdfsui(request):
       
        
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        sourcepdf_list = request.POST['sourcepdfs_list']
        
    except (KeyError):
    
        sourcepdf_list ='SourcePdf List Empty'

    try:
        the_user = request.POST['the_user']
        
    except (KeyError):
    
        the_user ='User Empty'
          
    try:
        user_name = request.POST['user_name']
        
    except (KeyError):
    
        user_name ='User To Assign Empty'
        
    try:
        user_group_name = request.POST['user_group']
        
    except (KeyError):
    
        user_group_name ='User Group assigned Empty'
    
    #print sourcepdf_list,the_user,company_name
    
    sourcepdf_list = str(sourcepdf_list)
    sourcepdf_list = sourcepdf_list.split('|');
    sourcepdf_list = sourcepdf_list[:-1]
    
    the_user = User.objects.filter(username=user_name)[0]
    
    with transaction.commit_on_success():
        for item in sourcepdf_list:
            if item:
                source = SourcePdf.objects.get(id=int(item))
                
                #the_user.assignedsourcepdfs.add(source)
                handles = source.assigndata.all().filter(assignedcompany__name = user_group_name).exclude(assigneduser__username = user_name)
                for handle in handles:
                   
                    if handle:
                        handle.assigneduser = the_user
                        handle.save()
                        source.save()
                        #the_user.save()
    
    return redirect('/admin/enersectapp/sourcepdf')    

def webcocoons(request):

    the_user = request.user

    if not the_user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="Arabic")[0]
    noneuser = User.objects.get(username="None")
    
    
    if the_user.groups.filter(name="TeamLeaders").exists():
        
        sourcepdfs_list = ""
       
        sourcepdfs_list = SourcePdfToHandle.objects.filter(assignedcompany=user_group).order_by()
                
        count_total = len(sourcepdfs_list)
        
        sourcepdfs_notassigned = SourcePdfToHandle.objects.filter(assigneduser=noneuser).order_by()
        sourcepdfs_notcomplete = SourcePdfToHandle.objects.filter(assignedcompany=user_group,checked="unchecked").order_by()
        
        count_notassigned = len(sourcepdfs_notassigned)
        count_notcomplete = len(sourcepdfs_notcomplete)
        count_assigned = count_total - count_notassigned
        
        count_done = count_total - count_notcomplete
        #count_done = sourcepdfs_list.filter(checked="checked").count()
               
        all_users_from_group_not_myself = User.objects.filter(groups=user_group).exclude(username=the_user.username)
       
        user_dictionary_values_list = []
        
        user_dictionary = { "name":"","assigned_count":0,"user_checked_count":0}
        
        count_total_categorizations = 0
        count_total_blank_or_not_blank = 0
                
        for index, item in enumerate(all_users_from_group_not_myself):
            user_dictionary = {}
            user_dictionary.update({"name":item.username})
            assigned_pdfs = SourcePdfToHandle.objects.filter(assigneduser=item)
            checked_count = assigned_pdfs.filter(checked="checked").count()
            assigned_unchecked_count = assigned_pdfs.exclude(checked="checked").count()
            user_profile = UserProfile.objects.get(user = item)
            completed_categorizations = len(user_profile.modifiedsourcepdfs_categorization_tool.all())+ len(user_profile.modifiedpdfs_categorization_tool.all())
            completed_blank_or_not_blank = len(user_profile.modifiedsourcepdfs_blank_or_not_tool.all())
            
            count_total_categorizations = count_total_categorizations+completed_categorizations
            count_total_blank_or_not_blank = count_total_blank_or_not_blank+completed_blank_or_not_blank
            
            user_dictionary.update({"assigned_unchecked_count":assigned_unchecked_count})
            
            user_dictionary.update({"checked_count":checked_count})
            
            user_dictionary.update({"id":item.id})
            
            user_dictionary.update({"completed_categorizations":completed_categorizations})
            
            user_dictionary.update({"completed_blank_or_not_blank":completed_blank_or_not_blank})
            
            user_dictionary_values_list.append(user_dictionary)
            
        
       
        context = {'user_dictionary_values_list':user_dictionary_values_list,
        'the_user':the_user.username,'user_group':user_group.name,
        'count_assigned':count_assigned,'count_done':count_done,'count_total':count_total,
        'count_notassigned':count_notassigned,'count_notcomplete':count_notcomplete,
        'count_total_categorizations':count_total_categorizations,'count_total_blank_or_not_blank':count_total_blank_or_not_blank}
        return render(request,'enersectapp/webcocoons.html',context)
       
    else:
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
       
    
@transaction.commit_manually    
def cocoons_save(request):

    try:
    
        the_user = request.user

        if not the_user.is_authenticated():
        
            return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    
        user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="Arabic")[0]
    
        sourcepdfstohandle_list = SourcePdfToHandle.objects.filter(assignedcompany=user_group).exclude(checked="checked")
    
        all_users_from_group_not_myself = User.objects.filter(groups=user_group).exclude(username=the_user.username)
    
        none_user = User.objects.get(username="None")
    
        count = 0
    
        #Resetting all the unassigned files to User None before making the real assignment
        #This ensures that you can actually delete an assignation without assigning to another user
    
    
        for item in sourcepdfstohandle_list:
            item.assigneduser = none_user
            item.save()
    
    
     
        #Real assignation. It starts with the assigning the appropriate number of documents to the first user
        #and proceeds from there on.
    
        for item in all_users_from_group_not_myself:
            maxNum = request.POST['name|'+item.username]
            maxNum = int(maxNum)
            temp_list = sourcepdfstohandle_list[count:count+maxNum]
            count = count + maxNum
            for to_assign in temp_list:
                to_assign.assigneduser = item
                to_assign.save()
    
    
        retval = HttpResponseRedirect(reverse('enersectapp:main', args=()))

        transaction.commit()
        return retval
        
    except:
        
        retval = HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
        transaction.rollback()
        return retval
    
        

def cocoons_new_teamuser(request):

    the_user = request.user;
    
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic")[0]

    if request.POST:
        username = request.POST['username']
        
        password = request.POST['password'].encode('ascii','replace')
        repeat_password = request.POST['repeat_password'].encode('ascii','replace')

        if password == repeat_password:
            user = User.objects.create_user(username, password)
            user.username = username
            user.set_password(repeat_password)
            user.groups.add(user_group)
            user.is_staff = True
            user.is_active = True
            user.save()
            return HttpResponseRedirect(reverse('enersectapp:webcocoons', args=()))
        else:
            return HttpResponseRedirect(reverse('enersectapp:main', args=()))


def randomqa_spider(request):

    the_user = request.user

    the_user_is_teamleader = False
    
    
    if not the_user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    
    if the_user.is_superuser == True or len(the_user.groups.filter(name="Auditors"))>0:
        
        
        '''lot_number = 0;
        
        pdf_records_list = PdfRecord.objects.none()
        
        company_list = Group.objects.exclude(name="NathanTeam").exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="INVENSIS")
        
        for company in company_list:
        
            pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrByCompany = company, sourcedoc_link__assigndata__lot_number = lot_number).distinct()
        
        
        
        pdf_id_list_to_randomize = []
        
        for item in pdf_records_list:
            
            pdf_id_list_to_randomize.append(int(item.id))
            
            
        random_id = random.choice(pdf_id_list_to_randomize)
        
        pdf_random_item = PdfRecord.objects.filter(id=random_id)[0]
        pdf_random_source = pdf_random_item.sourcedoc_link
        pdf_random_company = pdf_random_item.ocrrecord_link.OcrByCompany
        
        pdf_item_list = PdfRecord.objects.none()

     
        for company in company_list:
            
            pdf_item_list = pdf_item_list | PdfRecord.objects.filter(sourcedoc_link = pdf_random_source, sourcedoc_link__assigndata__assignedcompany=company).distinct()
            

        context = {'pdf_random_item':pdf_random_item,'pdf_item_list':pdf_item_list,"lot_number":lot_number}
        return render(request,'enersectapp/randomqa_spider.html',context)'''
    
    
        try:
            selected_modification_author = request.POST['selected_modification_author']
        except (KeyError):
            selected_modification_author =  "all"
            
        try:
            lot_number_check = request.POST['selected_lot']
        except (KeyError):
            lot_number_check =  "all"
     
        try:
            selected_user = request.POST['selected_user']
        except (KeyError):
            selected_user =  "all"
       
        try:
            selected_doctype = request.POST['selected_doctype']
        except (KeyError):
            selected_doctype =  "all"
        
        try:
            selected_company = request.POST['selected_company']
        except (KeyError):
            selected_company =  "all"
        
        try:
            selected_date = request.POST['selected_date']
        except (KeyError):
            selected_date =  "all"
        
        try:
            filters_panel_width = request.POST['filters_panel_width']
        except (KeyError):
            filters_panel_width =  ""
            
        try:
            filters_panel_height = request.POST['filters_panel_height']
        except (KeyError):
            filters_panel_height =  ""
        
        
        error_rate = 0
        
        pdf_records_list = PdfRecord.objects.none()
        
        user_company = the_user.groups.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic")[0]
   
        company_names_list = Group.objects.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="INVENSIS").order_by().values_list('name',flat=True)
   
        if selected_company == "all":
   
            company_list = Group.objects.exclude(name="NathanTeam").exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").exclude(name="INVENSIS")
        
        else:
        
            company_list = Group.objects.filter(name=selected_company)
        
        
        pdf_lot_number_distinct = SourcePdfToHandle.objects.none()
        
        for company in company_list:
           
            pdf_lot_number_distinct = pdf_lot_number_distinct | SourcePdfToHandle.objects.filter(assignedcompany = company,checked = 'checked').values('lot_number')
           
        
        pdf_lot_number_distinct = pdf_lot_number_distinct.distinct()
        
        
        lot_number_list = []
        pdf_lot_number_distinct_helper = []
        
        for item in pdf_lot_number_distinct:
            if item['lot_number'] not in lot_number_list:
                pdf_lot_number_distinct_helper.append(item)
                lot_number_list.append(item['lot_number'])
        
        pdf_lot_number_distinct = pdf_lot_number_distinct_helper
        
                
        
        #Filling a Lot Numbers in the Company List
        
        lot_number_list = []
        
        if lot_number_check == "all":
            for item in pdf_lot_number_distinct:
                if item['lot_number'] not in lot_number_list:
                    lot_number_list.append(item['lot_number'])
        
        else:
            lot_number_list.append(lot_number_check)
        
        
        pdf_author_distinct = SourcePdfToHandle.objects.none()
        
        for company in company_list:
        
            pdf_author_distinct = pdf_author_distinct | SourcePdfToHandle.objects.filter(assignedcompany = company,checked = 'checked').values('assigneduser__username')
        
        #Filling a Usernames in the Company list
        
        pdf_author_distinct = pdf_author_distinct.distinct()
        
        user_names_list = []
        
        if selected_user == "all":
            for item in pdf_author_distinct:
                user_names_list.append(item['assigneduser__username'])
            
            for lot_num in lot_number_list:
                for company in company_list:
                    pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrByCompany = company ,sourcedoc_link__assigndata__lot_number = lot_num,sourcedoc_link__assigndata__checked = "checked")
            
        else:
            user_names_list.append(selected_user)
        
            #Selecting All PdfRecords that have the Lots and Users in their fields in SourcePdfsToHandle
        
            for lot_num in lot_number_list:
                for user_name in user_names_list:
                    pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrAuthor__username = user_name,sourcedoc_link__assigndata__lot_number = lot_num,sourcedoc_link__assigndata__checked = "checked")
        
        
        #Making a list of Document Types and selecting the PdfRecords that are of that Document Type
        
        pdf_doctype_distinct = pdf_records_list.order_by().values('modified_document_type__name').distinct()
        
        pdf_doctype_list = []
        
        if selected_doctype != "all":
            pdf_doctype_list.append(selected_doctype)
           
            for doctype in pdf_doctype_list:
                doctype_class = SourceDocType.objects.filter(name=doctype)[0]
                pdf_records_list = pdf_records_list.filter(modified_document_type=doctype_class)
        
        
        #Getting rid of Duplicates
        
        pdf_records_list.distinct()
        
        #Compare the Time to the selected TimeFrame in Filter
        
        enddate = datetime.datetime.now()
        
        #Changing from naive to timezone to solve the Warning
        
        enddate = enddate.replace(tzinfo=timezone.utc)
        
        if selected_date == "today":
            startdate = enddate - timedelta(days=1)  

        elif selected_date == "lastdays":
            startdate = enddate - timedelta(days=4)  
        
        elif selected_date == "lastweek":
            startdate = enddate - timedelta(days=7)  
        
        elif selected_date == "lastmonth":
            startdate = enddate - timedelta(days=30)  
        
        elif selected_date == "lastmonths":
            startdate = enddate - timedelta(days=90)
        
        elif selected_date == "lastyear":
            startdate = enddate - timedelta(days=365)
            
        else:
            startdate = enddate - timedelta(days=10000)
            
        
        pdf_records_list = pdf_records_list.filter(modification_date__range=[startdate, enddate])

        
        #Saving the Audit Marks and making the necessary changes in the database
        #No changes if save_mark is None
        
        try:
            save_mark = request.POST['save_mark']
        except (KeyError):
            save_mark =  "None"
            
        if save_mark is not "None":
            
            if save_mark == "auditmarked_as_correct" or save_mark == "auditmarked_as_incorrect":
            
                try:
                    pdf_record_id = request.POST['pdf_record_id']
                except (KeyError):
                    pdf_record_id =  "None"
        
                if pdf_record_id is not "None":
                    recover_pdf = PdfRecord.objects.filter(id=pdf_record_id)[0]
                    recover_pdf.audit_mark = save_mark
                    recover_pdf.modification_author = the_user.username
                    recover_pdf.save()
        
            elif save_mark == "auditmarked_as_incorrect_reentry":
                
                incorrect_list = pdf_records_list.filter(audit_mark="auditmarked_as_incorrect")
                
                with transaction.commit_on_success():
                    for pdf in incorrect_list:

                        
                        pdf.audit_mark = "auditmarked_as_incorrect_reentry"
                        pdf.save()
        
            elif save_mark == "auditmarked_as_selection_reentry":
               
                with transaction.commit_on_success():
                    for pdf in pdf_records_list:

                        pdf.audit_mark = "auditmarked_as_selection_reentry"
                        pdf.save()
                    
        
        
        #Creating an Editor/Modification Authors List:
        
        modification_authors_selection = User.objects.filter(groups__name="NathanTeam")|User.objects.filter(groups__name="TeamLeaders")|User.objects.filter(groups__name="Auditors")
        modification_authors_list = modification_authors_selection.values_list('username',flat=True).order_by().distinct()
        
        #Selection by Modification Author
        
        pdf_authors_list = pdf_records_list
        
        if selected_modification_author!="all":
            pdf_authors_list = pdf_authors_list.filter(modification_author=selected_modification_author)
           
        pdf_total_count = len(pdf_records_list)
        
        pdf_correct_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_correct"))
        pdf_incorrect_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_incorrect"))
        pdf_reentry_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_incorrect_reentry")) + len(pdf_authors_list.filter(audit_mark="auditmarked_as_selection_reentry"))
        

        if pdf_correct_count!=0 and pdf_incorrect_count!=0:
            correct = float(pdf_correct_count)
            print correct
            incorrect = float(pdf_incorrect_count)
            print incorrect
            error_rate = incorrect/(correct + incorrect)*100
            error_rate = int(error_rate)
            
        pdf_records_list = pdf_records_list.exclude(audit_mark="auditmarked_as_correct").exclude(audit_mark="auditmarked_as_incorrect").exclude(audit_mark="auditmarked_as_incorrect_reentry").exclude(audit_mark="auditmarked_as_selection_reentry")
        
        pdf_id_list_to_randomize = []
        
        if len(pdf_records_list) > 0:
        
            '''for item in pdf_records_list:
                
                pdf_id_list_to_randomize.append(int(item.id))
            
            
                
            random_id = random.choice(pdf_id_list_to_randomize)
              
            pdf_item_list = PdfRecord.objects.filter(id=random_id)[:1]
            pdf_random_item = pdf_item_list[0]'''
            pdf_random_item = random.choice(pdf_records_list)
            pdf_item_list = PdfRecord.objects.filter(id=pdf_random_item.id)[:1]
            pdf_random_source = pdf_random_item.sourcedoc_link
            pdf_random_company = pdf_random_item.ocrrecord_link.OcrByCompany
            
            pdf_item_list = PdfRecord.objects.none()
            
            '''pdf_random_item = random.choice(pdf_records_list)
            pdf_item_list = PdfRecord.objects.filter(id=pdf_random_item.id)[:1]'''
            
            for company in company_list:
            
                pdf_item_list = pdf_item_list | PdfRecord.objects.filter(sourcedoc_link = pdf_random_source, sourcedoc_link__assigndata__assignedcompany=company).distinct()
            
        
        else:
        
            pdf_item_list = PdfRecord.objects.none()
            pdf_random_item = pdf_item_list
      
        
        
        context = {'user_type':"superuser",'pdf_random_item':pdf_random_item,
        'pdf_item_list':pdf_item_list,"lot_number":lot_number_check,
        'error_rate':error_rate,
        'pdf_doctype_distinct':pdf_doctype_distinct,'modification_authors_list':modification_authors_list,
        'pdf_total_count':pdf_total_count,'pdf_correct_count':pdf_correct_count,'company_names_list':company_names_list,
        'pdf_incorrect_count':pdf_incorrect_count,'pdf_reentry_count':pdf_reentry_count,
        'pdf_lot_number_distinct':pdf_lot_number_distinct,'pdf_author_distinct':pdf_author_distinct,
        'selected_user': selected_user,'selected_doctype': selected_doctype,'selected_company': selected_company,
        'selected_date':selected_date,'selected_modification_author':selected_modification_author,
        'filters_panel_width':filters_panel_width,
        'filters_panel_width':filters_panel_height}
        return render(request,'enersectapp/randomqa_spider.html',context)
    
    
    elif len(the_user.groups.filter(name="TeamLeaders")) >0:
     
        
        try:
            selected_modification_author = request.POST['selected_modification_author']
        except (KeyError):
            selected_modification_author =  "all"
        
        try:
            lot_number_check = request.POST['selected_lot']
        except (KeyError):
            lot_number_check =  "all"
        
        try:
            selected_user = request.POST['selected_user']
        except (KeyError):
            selected_user =  "all"
       
        try:
            selected_doctype = request.POST['selected_doctype']
        except (KeyError):
            selected_doctype =  "all"
        
        try:
            selected_company = request.POST['selected_company']
        except (KeyError):
            selected_company =  "all"
        
        try:
            selected_date = request.POST['selected_date']
        except (KeyError):
            selected_date =  "all"
        
        try:
            filters_panel_width = request.POST['filters_panel_width']
        except (KeyError):
            filters_panel_width =  ""
            
        try:
            filters_panel_height = request.POST['filters_panel_height']
        except (KeyError):
            filters_panel_height =  ""
        
        error_rate = 0
        
        pdf_records_list = PdfRecord.objects.none()
        
        user_company = the_user.groups.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic")[0]
   
        
        pdf_lot_number_distinct = SourcePdfToHandle.objects.filter(assignedcompany = user_company,checked = 'checked').order_by().values('lot_number').distinct()
        
        #pdf_author_distinct = PdfRecord.objects.filter(ocrrecord_link__OcrByCompany = user_company).values('sourcedoc_link__assigndata__assigneduser__username').distinct()

        
        #Filling a Lot Numbers in the Company List
        
        lot_number_list = []
        
        if lot_number_check == "all":
           
            for item in pdf_lot_number_distinct:
                lot_number_list.append(item['lot_number'])
        
        else:
            lot_number_list.append(lot_number_check)
        
        
        pdf_author_distinct = SourcePdfToHandle.objects.filter(assignedcompany = user_company,checked = 'checked').order_by().values('assigneduser__username').distinct()
        
        #Filling a Usernames in the Company list
        
        user_names_list = []
        
        if selected_user == "all":
            for item in pdf_author_distinct:
                user_names_list.append(item['assigneduser__username'])
            
            #Selecting All PdfRecords that have the Lots and Users in their fields in SourcePdfsToHandle
            for lot_num in lot_number_list:
                pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrByCompany = user_company ,sourcedoc_link__assigndata__lot_number = lot_num,sourcedoc_link__assigndata__checked = "checked")
                
        else:
            user_names_list.append(selected_user)
        
            for lot_num in lot_number_list:
                for user_name in user_names_list:
                    pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrAuthor__username = user_name,sourcedoc_link__assigndata__lot_number = lot_num,sourcedoc_link__assigndata__checked = "checked")
        
        
        pdf_doctype_distinct = pdf_records_list.order_by().values('modified_document_type__name').distinct()
        
        pdf_doctype_list = []
        
        if selected_doctype != "all":
            pdf_doctype_list.append(selected_doctype)
           
            for doctype in pdf_doctype_list:
                doctype_class = SourceDocType.objects.filter(name=doctype)[0]
                pdf_records_list = pdf_records_list.filter(modified_document_type=doctype_class) 
        
        
        #Getting rid of Duplicates
        
        pdf_records_list.distinct()
        
        #Compare the Time to the selected TimeFrame in Filter
        
        enddate = datetime.datetime.now()
        
        #Changing from naive to timezone to solve the Warning
        
        enddate = enddate.replace(tzinfo=timezone.utc)
        
        if selected_date == "today":
            startdate = enddate - timedelta(days=2)  

        elif selected_date == "lastdays":
            startdate = enddate - timedelta(days=4)  
        
        elif selected_date == "lastweek":
            startdate = enddate - timedelta(days=7)  
        
        elif selected_date == "lastmonth":
            startdate = enddate - timedelta(days=30)  
        
        elif selected_date == "lastmonths":
            startdate = enddate - timedelta(days=90)
        
        elif selected_date == "lastyear":
            startdate = enddate - timedelta(days=365)
            
        else:
            startdate = enddate - timedelta(days=10000)
            
        
        pdf_records_list = pdf_records_list.filter(modification_date__range=[startdate, enddate])

        
        #Saving the Audit Marks and making the necessary changes in the database
        #No changes if save_mark is None
        
        try:
            save_mark = request.POST['save_mark']
        except (KeyError):
            save_mark =  "None"
            
        if save_mark is not "None":
            
            if save_mark == "auditmarked_as_correct" or save_mark == "auditmarked_as_incorrect":
            
                try:
                    pdf_record_id = request.POST['pdf_record_id']
                except (KeyError):
                    pdf_record_id =  "None"
        
                if pdf_record_id is not "None":
                    recover_pdf = PdfRecord.objects.filter(id=pdf_record_id)[0]
                    recover_pdf.modification_author = the_user.username
                    recover_pdf.audit_mark = save_mark
                    recover_pdf.save()
        
            elif save_mark == "auditmarked_as_incorrect_reentry":
                
                incorrect_list = pdf_records_list.filter(audit_mark="auditmarked_as_incorrect")
                
                with transaction.commit_on_success():
                    for pdf in incorrect_list:

                        
                        pdf.audit_mark = "auditmarked_as_incorrect_reentry"
                        pdf.save()
        
            elif save_mark == "auditmarked_as_selection_reentry":
               
                with transaction.commit_on_success():
                    for pdf in pdf_records_list:

                        pdf.audit_mark = "auditmarked_as_selection_reentry"
                        pdf.save()
                    
        
        
        #Creating an Editor/Modification Authors List:
        
        modification_authors_selection = User.objects.filter(groups=user_company).filter(groups__name="TeamLeaders")
        modification_authors_list = modification_authors_selection.values_list('username',flat=True).order_by().distinct()
        
        #Selection by Modification Author
        
        pdf_authors_list = pdf_records_list
        
        if selected_modification_author!="all":
            pdf_authors_list = pdf_records_list.filter(modification_author=selected_modification_author)
            
           
        pdf_total_count = len(pdf_records_list)
        
        pdf_correct_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_correct"))
        pdf_incorrect_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_incorrect"))
        pdf_reentry_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_incorrect_reentry")) + len(pdf_records_list.filter(audit_mark="auditmarked_as_selection_reentry"))
        
        if pdf_correct_count!=0 and pdf_incorrect_count!=0:
            correct = float(pdf_correct_count)
            incorrect = float(pdf_incorrect_count)
            error_rate = incorrect/(correct + incorrect)*100
            error_rate = int(error_rate)
            
        
        pdf_records_list = pdf_records_list.exclude(audit_mark="auditmarked_as_correct").exclude(audit_mark="auditmarked_as_incorrect").exclude(audit_mark="auditmarked_as_incorrect_reentry").exclude(audit_mark="auditmarked_as_selection_reentry").exclude(audit_mark="duplicatemarked_reentered")
        
        pdf_id_list_to_randomize = []
        
        if len(pdf_records_list) > 0:
        
            '''for item in pdf_records_list:
                
                pdf_id_list_to_randomize.append(int(item.id))
 
            random_id = random.choice(pdf_id_list_to_randomize)
              
            pdf_item_list = PdfRecord.objects.filter(id=random_id)[:1]'''
            pdf_random_item = random.choice(pdf_records_list)
            pdf_item_list = PdfRecord.objects.filter(id=pdf_random_item.id)[:1]
        
        else:
        
            pdf_item_list = PdfRecord.objects.none()
            pdf_random_item = pdf_item_list
        
        
        context = {'user_type':"TeamLeader",'pdf_random_item':pdf_random_item,
        'pdf_item_list':pdf_item_list,"lot_number":lot_number_check,'error_rate':error_rate,
        'pdf_doctype_distinct':pdf_doctype_distinct,'modification_authors_list':modification_authors_list,
        'pdf_total_count':pdf_total_count,'pdf_correct_count':pdf_correct_count,
        'pdf_incorrect_count':pdf_incorrect_count,'pdf_reentry_count':pdf_reentry_count,
        'pdf_lot_number_distinct':pdf_lot_number_distinct,'pdf_author_distinct':pdf_author_distinct,
        'selected_user': selected_user,'selected_doctype': selected_doctype,
        'selected_date':selected_date,'selected_modification_author':selected_modification_author,
        'filters_panel_width':filters_panel_width,
        'filters_panel_width':filters_panel_height}
        return render(request,'enersectapp/randomqa_spider.html',context)
    
    else:
    
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))            


def categorization_tool(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    #Mode indicates if the Pdfs to categorize are taken from the "No Category" Pool on the Source Pdfs, the "Other" Pool on the Entries, or All Entries.
    
    try:
        mode = request.POST['mode']
        
    except (KeyError):
    
        mode='other_mode'
        
    try:
        show_progress = request.POST['show_progress']
        
    except (KeyError):
    
        show_progress='dont_show'
           
    try:
        save_id = request.POST['save_id']
        
    except (KeyError):
    
        save_id='NoId'
        
    try:
        doctype = request.POST['doctype']
        
    except (KeyError):
    
        doctype='NoDocType'
        
        
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic")[0]
    user_profile = UserProfile.objects.get(user = the_user)
    
    if the_user.is_superuser == False and user_group.name != "Enersect_Berlin":
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
    
    sourcepdfs_list = SourcePdf.objects.none()
    count_uncategorized = "No Uncategorized in this Mode"
    count_other = "No Others in this Mode"
    count_total = 0
    
    types_list = SourceDocType.objects.exclude(name="other").exclude(name="recuperation").exclude(name="blank probable").exclude(name="contract page 1").exclude(name="contract page X").order_by('name')
    
    if(doctype!="NoDocType"):
    
        doctype = doctype.lower()
        #Prevent having spaces after the name
        doctype = doctype.rstrip()
        
                    
        if doctype == "invoice/facture":
            doctype = "invoice"
            
        if doctype == "receipt/recu":
            doctype = "receipt"
        
        
    if mode == "uncategorized_mode":
        #job1\scan1~2013_06_08_11_00_00_248.pdf
        if(save_id!="NoId" and doctype!="NoDocType"): 
            source_to_change = SourcePdf.objects.filter(id=save_id)[0]
            
            doctype_class = SourceDocType.objects.filter(name=doctype)[:1]
            if (len(doctype_class)>0):
                doctype_class=doctype_class[0]
            else:
                doctype_class = SourceDocType()
                doctype_class.name = doctype
                doctype_class.pretty_name = doctype
                doctype_class.save()
            
            source_to_change.document_type=doctype
            source_to_change.modified_document_type = doctype_class
            source_to_change.modification_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            source_to_change.modification_doctype_author=the_user
            source_to_change.save()
            
            if len(user_profile.modifiedsourcepdfs_categorization_tool.filter(pk=source_to_change.pk))==0:
                user_profile.modifiedsourcepdfs_categorization_tool.add(source_to_change)
                user_profile.save()
    
        #count_total = len(SourcePdf.objects.all())
        pdfrecords_list = PdfRecord.objects.none()
        doctype_uncategorized = SourceDocType.objects.get(name="uncategorized")
        sourcepdfs_list = SourcePdf.objects.filter(modified_document_type=doctype_uncategorized).values('id','modified_document_type__name','job_directory','filename').order_by()
        count_uncategorized = len(sourcepdfs_list)

        if (count_uncategorized>0):
         
            random_int = random.randrange(0,count_uncategorized,1)
            sourcepdfs_item = sourcepdfs_list[random_int]

        else:
            sourcepdfs_item = []
        
        chosen_item =  sourcepdfs_item
    
    
    elif mode == "other_mode":
    
        if(save_id!="NoId" and doctype!="NoDocType"): 
            pdfrecord_to_change = PdfRecord.objects.filter(id=save_id)[0]
            doctype_class = SourceDocType.objects.filter(name=doctype)[:1]
            if (len(doctype_class)>0):
                doctype_class=doctype_class[0]
            else:
                doctype_class = SourceDocType()
                doctype_class.name = doctype
                doctype_class.pretty_name = doctype
                doctype_class.save()
                
            pdfrecord_to_change.modified_doctype_from=doctype
            pdfrecord_to_change.modified_document_type = doctype_class
            pdfrecord_to_change.modification_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            pdfrecord_to_change.modification_doctype_author=the_user
            pdfrecord_to_change.save()
            
            if len(user_profile.modifiedpdfs_categorization_tool.filter(pk=pdfrecord_to_change.pk))==0:
                user_profile.modifiedpdfs_categorization_tool.add(pdfrecord_to_change)
                user_profile.save()
    
        sourcepdfs_list = SourcePdf.objects.none()
        doctype_other = SourceDocType.objects.get(name="other")
        pdfrecords_list = PdfRecord.objects.filter(modified_document_type=doctype_other).values('id','modified_document_type__name','sourcedoc_link__job_directory','sourcedoc_link__filename').order_by()
        count_other = len(pdfrecords_list)
    
        if (count_other>0):
            random_int = random.randrange(0,count_other,1)
            pdfrecords_item = pdfrecords_list[random_int]
            
        else:
            pdfrecords_item = []
        
        chosen_item =  pdfrecords_item
    
    else:
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
  
    
    count_this_user = len(user_profile.modifiedsourcepdfs_categorization_tool.all())+ len(user_profile.modifiedpdfs_categorization_tool.all())
    show_progress_user = 'Completed by you: '+str(count_this_user)
    
  
    context = {'mode':mode,'user_group':user_group.name,'types_list':types_list,
    'chosen_item':chosen_item,'the_user':the_user.username,'count_other':count_other,
    'count_uncategorized':count_uncategorized,'count_total':count_total,'show_progress_user':show_progress_user}
    
    return render(request,'enersectapp/categorization_tool.html',context)

    
def blank_or_not_blank(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    try:
        show_progress = request.POST['show_progress']
        
    except (KeyError):
    
        show_progress='dont_show'
           
    try:
        save_id = request.POST['save_id']
        
    except (KeyError):
    
        save_id='NoId'
        
    try:
        success_message = request.POST['success_message']
        
    except (KeyError):
    
        success_message='' 
        
    try:
        blank_or_not_blank = request.POST['blank_or_not_blank']
        
    except (KeyError):
    
        blank_or_not_blank='NoChoice'
          
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic")[0]
    user_profile = UserProfile.objects.get(user = the_user)
    
    if the_user.is_superuser == False and user_group.name != "Enersect_Berlin":
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
    sourcepdfs_list = SourcePdf.objects.none()
    count_blank_probable = "No Blank Probables Left"

    count_total = 0
    
    if blank_or_not_blank != "NoChoice" and blank_or_not_blank != "RollBack":
        #job1\scan1~2013_06_08_11_00_00_248.pdf
        if(save_id!="NoId"): 
        
            source_to_change = SourcePdf.objects.filter(id=save_id)[0]
            
            doctype_class = SourceDocType.objects.filter(name=blank_or_not_blank)[:1]
            
            if (len(doctype_class)>0):
                doctype_class=doctype_class[0]
            else:
                doctype_class = SourceDocType()
                doctype_class.name = blank_or_not_blank
                doctype_class.pretty_name = blank_or_not_blank
                doctype_class.save()
            
            source_to_change.document_type= blank_or_not_blank
            source_to_change.modified_document_type = doctype_class
            source_to_change.modification_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            source_to_change.modification_doctype_author=the_user
            source_to_change.save()
            
            if len(user_profile.modifiedsourcepdfs_blank_or_not_tool.filter(pk=source_to_change.pk))==0:
                user_profile.modifiedsourcepdfs_blank_or_not_tool.add(source_to_change)
                user_profile.save()
                
    
    #count_total = len(SourcePdf.objects.all())
    

    doctype_blankprobable = SourceDocType.objects.get(name="blank probable")
    sourcepdfs_list = SourcePdf.objects.filter(modified_document_type=doctype_blankprobable).values('id','modified_document_type__name','job_directory','filename').order_by()
    count_blank_probable = len(sourcepdfs_list)

    if (count_blank_probable>0):
         
        random_int = random.randrange(0,count_blank_probable,1)
        source_item = sourcepdfs_list[random_int]

    else:
        source_item = []
        
    chosen_item =  source_item
  
    
    if blank_or_not_blank == "RollBack":
        
        all_items = user_profile.modifiedsourcepdfs_blank_or_not_tool.all().order_by('-modification_doctype_date')
        length = len(all_items)
        last_item = all_items[0]
        blank_probable_type = SourceDocType.objects.get(name="blank probable")
        last_item.modified_document_type = blank_probable_type
        last_item.save()
        user_profile.modifiedsourcepdfs_blank_or_not_tool.remove(last_item)
        chosen_item = last_item
        
    
    count_this_user = len(user_profile.modifiedsourcepdfs_blank_or_not_tool.all())
    
    show_progress_user = 'Completed by you: '+str(count_this_user)
        
  
    if blank_or_not_blank != "NoChoice" and blank_or_not_blank != "RollBack":
  
        if blank_or_not_blank == "blank":
        
            success_message = "The previous document was saved as BLANK"
            
        else:
        
            type = blank_or_not_blank.upper()
            success_message = "The previous document was saved as "+type+" (NOT BLANK)"
    
  
    context = {'user_group':user_group.name,'success_message':success_message,
    'chosen_item':chosen_item,'the_user':the_user.username,
    'count_blank_probable':count_blank_probable,'count_total':count_total,'show_progress_user':show_progress_user}
    
    return render(request,'enersectapp/blank_or_not_blank.html',context)

def sudo_assignsourcepdfsui_by_doctype_and_number(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or the_user.is_superuser == False :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        company_name = request.POST['company_name']
        
    except (KeyError):
    
        company_name='NoCompanyName'
      
    try:
        doctype_name = request.POST['doctype_name']
        
    except (KeyError):
    
        doctype_name='NoDocType'
        
    try:
        num_toassign = request.POST['num_toassign']
        
    except (KeyError):
    
        num_toassign='0'
    
    try:
        save_data = request.POST['save_data']
        
    except (KeyError):
    
        save_data='dont_save'
    
    #print "DonE!----------------1"
    success_message = ""
    
    none_user = User.objects.get(username="None")
    
    num_toassign = int(num_toassign)
    
    company_names_list = Group.objects.exclude(name="INVENSIS").exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic").values_list('name',flat=True).distinct()
    doctype_names_list = []
    #print "DonE!----------------2"
    number_follow_assign_criteria = 0
    number_docs_not_in_company = 0
    #print "DonE!----------------3"
    lot_number_list = SourcePdfToHandle.objects.exclude(assignedcompany__name="TestGroup").order_by().values_list('lot_number',flat=True).distinct()
    #print "DonE!----------------4"            
    max_lotnum = int(max(lot_number_list))
    #print "DonE!----------------5"
    
    
    if company_name != "NoCompanyName":
        #print "DonE!----------------6"
        the_company = Group.objects.get(name=company_name)
        #print "DonE!----------------7"
        if doctype_name != "NoDocType":
        
            #Inside this If I will take up to the selected number of documents to assign
            #from the chosen Company and assign them to the chosen Company, to the helper
            #user "None", and mark them with a Lot Number equal to the maximum existing Lot Number + 1
            #print "DonE!----------------8"
            
            the_doctype =  SourceDocType.objects.get(name=doctype_name)
            
            if num_toassign !=0 and save_data=="save_data":

                docs_to_assign = SourcePdf.objects.exclude(assigndata__assignedcompany = the_company).filter(modified_document_type = the_doctype).order_by()[:num_toassign]
                #print "DonE!----------------9"
                with transaction.commit_on_success():
                    for source in docs_to_assign:
                        if source:
                            tohandle = SourcePdfToHandle(assignedcompany=the_company,assigneduser=none_user,lot_number=max_lotnum+1)
                            tohandle.save()
                            source.assigndata.add(tohandle)
                            source.save()

                    #print "DonE!----------------10"
                    max_lotnum = max_lotnum+1
                    success_message = str(len(docs_to_assign)) + " Documents from " + doctype_name + " were assigned to " + company_name + " as Lot "+ str(max_lotnum) + "."
                    #print "DonE!----------------11"
                            
            the_doctype =  SourceDocType.objects.get(name=doctype_name)
            #print "DonE!----------------12"
            docs_not_in_company = SourcePdf.objects.exclude(assigndata__assignedcompany = the_company).order_by()
            #print "DonE!----------------13"
            docs_in_doctype = docs_not_in_company.filter(modified_document_type = the_doctype).order_by()
            #print "DonE!----------------14"
            number_follow_assign_criteria = len(docs_in_doctype)
            #print "DonE!----------------15"
            number_docs_not_in_company = len(docs_not_in_company)
            #print "DonE!----------------16"
            doctype_names_list = docs_not_in_company.values_list('modified_document_type__name',flat=True).distinct()
            #print "LENGTH OF DOCTYPE -------->" + str(len(doctype_names_list))
            #print "DonE!----------------17"
        else:
            #print "DonE!----------------18"
            docs_not_in_company = SourcePdf.objects.exclude(assigndata__assignedcompany = the_company).order_by()
            #print "DonE!----------------19"
            number_follow_assign_criteria = 0
            number_docs_not_in_company = len(docs_not_in_company)
            
            #print "DonE!----------------20"
            
            doctype_names_list = docs_not_in_company.values_list('modified_document_type__name',flat=True).distinct()
            #print "LENGTH OF DOCTYPE2 -------->" + str(len(doctype_names_list))
            #print "DonE!----------------21"
            
    
    #print "DonE!----------------22"
    #print len(doctype_name)
    #print len(company_name)
    #print len(success_message)
    #print number_follow_assign_criteria
    #print number_docs_not_in_company
    #print len(doctype_names_list)
    #print max_lotnum
    #print len(company_names_list)
    #print len(doctype_names_list)
    
    context = {'doctype_name':doctype_name,'company_name':company_name,'success_message':success_message,
    'number_follow_assign_criteria':number_follow_assign_criteria,'number_docs_not_in_company':number_docs_not_in_company,
    'max_lotnum':max_lotnum,'company_names_list':company_names_list,'doctype_names_list':doctype_names_list}
    #print "DonE!----------------23"
    return render(request,'enersectapp/sudo_assign_by_doctype_and_number.html',context)
        

def progress_report(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or (the_user.is_superuser == False and the_user.username != "JamesTL") :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        export_mark = request.POST['export_mark']
        
    except (KeyError):
    
        export_mark='none'
    
    super_group = Group.objects.get(name="NathanTeam")
    test_group = Group.objects.get(name="TestGroup")
    invensis_group = Group.objects.get(name="INVENSIS")
    
    #Number of total Source Documents
    
    source_documents_all = SourcePdf.objects.all().values('filename','modified_document_type').distinct()
    
    total_source_documents = len(source_documents_all)
    
    #Number of Source Documents that have a category other than "Uncategorized" or "Other"
    
    total_with_doctype = len(source_documents_all.exclude(modified_document_type__name="uncategorized").exclude(modified_document_type__name="other"))
    
    
    # Number of total documents entered
    
    total_pdf_entered_list = PdfRecord.objects.exclude(audit_mark="duplicatemarked_reentered").exclude(ocrrecord_link__OcrByCompany=test_group).exclude(ocrrecord_link__OcrByCompany=invensis_group).exclude(ocrrecord_link__OcrByCompany=super_group).values('ocrrecord_link','modified_document_type','sourcedoc_link','status','audit_mark').order_by().distinct()
    
    total_pdf_entered = len(total_pdf_entered_list)
    
    #Groups and names of the Groups
    
    #Documents entered by each Group
    

    company_names_list = total_pdf_entered_list.values_list('ocrrecord_link__OcrByCompany__name',flat=True).order_by().distinct()
    
    company_names_and_values_list = []
    
    for item in company_names_list:
    
        name = item
        count = len(total_pdf_entered_list.filter(ocrrecord_link__OcrByCompany__name = name).values('ocrrecord_link').order_by().distinct())
        dictionary_item = {}
        dictionary_item['name'] = name
        dictionary_item['count'] = count
        company_names_and_values_list.append(dictionary_item)

    
    #List of Document Types entered and how many of each
    
    document_types_list = total_pdf_entered_list.values_list('modified_document_type__name',flat=True).distinct()
    
    # Number of each Doctype entered
 
    document_types_names_and_values_list = []
    
    for item in document_types_list:
    
        name = item
        count = len(total_pdf_entered_list.filter(modified_document_type__name = name).values('modified_document_type','id').order_by().distinct())
        dictionary_item = {}
        dictionary_item['name'] = name
        dictionary_item['count'] = count
        document_types_names_and_values_list.append(dictionary_item)
    
    
    # Number of total documents linked

    
    total_linked_documents = len(total_pdf_entered_list.filter(status = "pdf_linked"))
   
   
   
    # Number of total documents rejected
    # Number of entries divided by Country
    
    if export_mark == "export_csv":
    
        date = datetime.datetime.now().strftime("%d_%m_%Y")
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="progress_report_'+date+'".csv"'

        writer = csv.writer(response)
        writer.writerow(['               ', 'Total Number Of:', '               '])
        writer.writerow(['Source Documents', total_source_documents, '               '])
        writer.writerow(['Documents With an Identified Document Type', total_with_doctype, '               '])
        writer.writerow(['               ','               ','               '])
        writer.writerow(['Documents Entries Made', total_pdf_entered, '               '])
        writer.writerow(['Documents Entries Linked to a Record', total_linked_documents, '               '])
        writer.writerow(['               ','               ','               '])
        for item in company_names_and_values_list:
            writer.writerow(['Entries made by '+item['name'], item['count'], '               '])
        writer.writerow(['               ','               ','               '])    
        for item in document_types_names_and_values_list:
            writer.writerow(['Entries with Document Type '+item['name'], item['count'], '               '])
        
        
        return response
        #return HttpResponseRedirect(reverse('enersectapp:progress_report', args=()))  
    
    else:
    
        context = {'total_source_documents':total_source_documents,'total_with_doctype':total_with_doctype,
        'total_pdf_entered':total_pdf_entered,'company_names_and_values_list':company_names_and_values_list,
        'document_types_names_and_values_list':document_types_names_and_values_list,
        'total_linked_documents':total_linked_documents,'the_user':the_user}
        #print "DonE!----------------23"
        return render(request,'enersectapp/progress_report.html',context)
    

def category_changer(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or the_user.is_superuser == False :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        save_mark = request.POST['save_mark']
        
    except (KeyError):
    
        save_mark='none'
        
    try:
        type1 = request.POST['type1']
        
    except (KeyError):
    
        type1='none'
        
    try:
        type2 = request.POST['type2']
        
    except (KeyError):
    
        type2='none'
        
    try:
        type3 = request.POST['type3']
        
    except (KeyError):
    
        type3='none'
      
    types_list = SourceDocType.objects.all().order_by('name','id')
    success_message = ""
    
    if save_mark == "delete_mark" and type3!="none":
    
        try:
            type3_doctype = SourceDocType.objects.filter(name=type3)[0]
        except:
            type3_doctype = ""
            
        if type3_doctype:    
            all_sources_type3 = SourcePdf.objects.filter(modified_document_type = type3_doctype)
            all_pdfs_type3 = PdfRecord.objects.filter(modified_document_type = type3_doctype)
        
            if len(all_sources_type3)==0 and len(all_pdfs_type3)==0:
                type3_doctype.delete()
        
        return HttpResponseRedirect(reverse('enersectapp:category_changer', args=()))
    
    if save_mark == "save_mark" and type1!="none" and type2 !="none":
    
        type1_doctype = SourceDocType.objects.filter(name=type1)[0]
        type2_doctype = SourceDocType.objects.filter(name=type2)[0]
            
        all_sources_type1 = SourcePdf.objects.filter(modified_document_type = type1_doctype)
        all_pdfs_type1 = PdfRecord.objects.filter(modified_document_type = type1_doctype)
        
        with transaction.commit_on_success():  
            for item in all_sources_type1:
                
                if item:
                    item.modified_document_type = type2_doctype
                    item.original_document_type_string = type1
                    item.save()
        
            for pdf in all_pdfs_type1:
                
                if pdf:
                    pdf.modified_document_type = type2_doctype
                    pdf.modified_doctype_from = type1
                    pdf.save()
        
 
        success_message = "Changed all documents with type "+type1+" to type "+type2
            

    context = {'types_list':types_list,'the_user':the_user,'success_message':success_message}
    #print "DonE!----------------23"
    return render(request,'enersectapp/category_changer.html',context)
    

def arabic_memo_edit(request):
    
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="Arabic")[0]
    user_profile = UserProfile.objects.get(user = the_user)
    is_arabic_group = the_user.groups.filter(name = "Arabic")
    
    if not request.user.is_authenticated() or (the_user.is_superuser == False and len(is_arabic_group) != 1) :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
       
    try:
        save_id = request.POST['save_id']
        
    except (KeyError):
    
        save_id='NoId'
        
    try:
        success_message = request.POST['success_message']
        
    except (KeyError):
    
        success_message='' 
        
    try:
        translation_memo = request.POST['translation_memo']
    except:
        translation_memo = "NoTranslationField"
        
    try:
        save_mark = request.POST['save_mark']
    except:
        save_mark = "NoSaveMark"
          
    
    
    if the_user.is_superuser == False and user_group.name != "Enersect_Berlin":
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
    pdfrecords_list = PdfRecord.objects.none()
    count_arabic = "No Arabics Left"

    count_total = 0
    
    if save_mark == "save_mark":
        #job1\scan1~2013_06_08_11_00_00_248.pdf
        if(save_id!="NoId"): 
        
            pdf_to_change = PdfRecord.objects.filter(id=save_id)[0]
            
            pdf_to_change.ocrrecord_link.Translation_Notes = translation_memo
            pdf_to_change.ocrrecord_link.save()
            
            pdf_to_change.modification_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            pdf_to_change.modification_author=the_user
            pdf_to_change.translated = "arabic translation"
            pdf_to_change.save()
            
            if len(user_profile.modifiedpdfs_translated_arabic.filter(pk=pdf_to_change.pk))==0:
                user_profile.modifiedpdfs_translated_arabic.add(pdf_to_change)
                user_profile.save()
           
                
    
    #count_total = len(SourcePdf.objects.all())        
    
    count_this_user = len(user_profile.modifiedpdfs_translated_arabic.all())
    
    show_progress_user = 'Completed by you: '+str(count_this_user)
        
    #pdfrecords_list = PdfRecord.objects.filter(    
  
    pdfrecords_list = PdfRecord.objects.filter(ocrrecord_link__ContainsArabic = "Yes").filter(translated = "no").order_by()
    
    chosen_item = pdfrecords_list[0]
    
    count_arabic = len(pdfrecords_list)
  
  
    context = {'user_group':user_group.name,'success_message':success_message,
    'chosen_item':chosen_item,'the_user':the_user.username,
    'count_arabic':count_arabic,'count_total':count_total,'show_progress_user':show_progress_user}
    
    return render(request,'enersectapp/arabic_memo_edit.html',context)    
    
    