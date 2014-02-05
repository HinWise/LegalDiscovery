
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


import random

def arabic_memo_edit(request):
    
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
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
            if translation_memo == "needs arabic translation" or translation_memo == "not worth arabic translation":
                pdf_to_change.translated = translation_memo
            else:
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