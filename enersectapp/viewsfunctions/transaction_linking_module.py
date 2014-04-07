
from enersectapp.models import *

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

import random

def transaction_linking(request):
    
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    the_user = request.user
   
    
    
   
    try:
        entry_item = PdfRecord.objects.exclude(entrylinks_link = None).order_by()[0]
        entry_item_pk = entry_item.pk
        entrylinks_pk = entry_item.entrylinks_link.pk
        
        high_candidates_list = entry_item.entrylinks_link.high_candidates_list.all().order_by().values('pk')
        medium_candidates_list = entry_item.entrylinks_link.medium_candidates_list.all().order_by().values('pk')
        low_candidates_list = entry_item.entrylinks_link.low_candidates_list.all().order_by().values('pk')
        excluded_candidates_list = entry_item.entrylinks_link.excluded_candidates_list.all().order_by().values('pk')
        
    except:
    
        corpus_entries = PdfRecord.objects.all().order_by()

        corpus_entries_length = corpus_entries.count()

        entry_item_index = random.randint(0,corpus_entries_length)
        entry_item = corpus_entries[entry_item_index]
        entry_item_pk = entry_item.pk
        #entry_item = PdfRecord.objects.all().order_by()[0]
        entrylinks_pk = 0
        high_candidates_list =[]
        medium_candidates_list = []
        low_candidates_list = []
        excluded_candidates_list = []
    

    #sample_transactions = TransactionTable.objects.all().order_by()[14698:14705]
    sample_transactions = TransactionTable.objects.all().order_by()[14600:14607]
    
    searchtags = ['amount','doctype','date','account','memo','reftran','libelle','account']
    number_of_searchtags = len(searchtags)
   
    if number_of_searchtags>8:
        number_of_searchtags = 8

      
    context = {"the_user":the_user,'entry_item':entry_item,
                'entry_item_pk':entry_item_pk,
                'entrylinks_pk':entrylinks_pk,'high_candidates_list':high_candidates_list,'medium_candidates_list':medium_candidates_list,
                'low_candidates_list':low_candidates_list,'excluded_candidates_list':excluded_candidates_list,'number_of_searchtags': number_of_searchtags,
                'searchtags':searchtags,'sample_transactions':sample_transactions}
    return render(request,'enersectapp/transaction_linking.html',context)