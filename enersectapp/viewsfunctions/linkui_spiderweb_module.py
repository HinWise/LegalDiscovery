
from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response


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