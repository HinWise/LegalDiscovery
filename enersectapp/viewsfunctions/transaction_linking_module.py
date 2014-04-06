
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
   
    
    corpus_entries = PdfRecord.objects.all().order_by()

    corpus_entries_length = corpus_entries.count()

    entry_item_index = random.randint(0,corpus_entries_length)
    entry_item = corpus_entries[entry_item_index]
    print entry_item.pk
   
    entry_item = PdfRecord.objects.exclude(entrylinks_link = None).order_by()[0]
    
    entry_item_pk = entry_item.pk
    entrylinks_pk = entry_item.entrylinks_link.pk
    
    high_candidates_list = entry_item.entrylinks_link.high_candidates_list.all().order_by().values('pk')
    medium_candidates_list = entry_item.entrylinks_link.medium_candidates_list.all().order_by().values('pk')
    low_candidates_list = entry_item.entrylinks_link.low_candidates_list.all().order_by().values('pk')
    excluded_candidates_list = entry_item.entrylinks_link.excluded_candidates_list.all().order_by().values('pk')
    
    print entry_item.entrylinks_link.high_candidates_list.all()
   
    sample_transaction = TransactionTable.objects.all().order_by()[14700]
   
    dataset = SourcePdf.objects.all().order_by()[100:107]#[10461:10468]
    
    main_dict = {}
    
    main_dict["name"] = "List of Transactions"
    
    temp_list = []
    
    count = 0
    
    for item_transaction in dataset:
    
        count += 1
        
        temp_dict = {}
        
        temp_dict["name"] = "Transaction "+str(count)
        
        temp_sublist = []
        
        temp_subdict = {}
        temp_subdict["name"] = "PK = "+str(item_transaction.pk)
        temp_sublist.append(temp_subdict)
        temp_subdict = {}
        temp_subdict["name"] = "Job Directory = "+str(item_transaction.job_directory)
        temp_sublist.append(temp_subdict)
        temp_subdict = {}
        temp_subdict["name"] = "Filename = "+str(item_transaction.filename)
        temp_sublist.append(temp_subdict)
        
        temp_subdict = {}
        temp_subdict["name"] = "Assigned Handles"
        
        temp_assigneddatalist = []
        
        count_handles = 0
        
        for handle in item_transaction.assigndata.all():
        
            count_handles += 1
            
            temp_handles_subdict = {}
            temp_handles_subdict["name"] = "Assigned Handle PK "+str(handle.pk)
        
            temp_handles_sublist = []
        
            temp_assigneddatadict = {}
            temp_assigneddatadict["name"] = "Lot Number = "+str(handle.lot_number)
            temp_handles_sublist.append(temp_assigneddatadict)
        
            temp_assigneddatadict = {}
            temp_assigneddatadict["name"] = "Company = "+str(handle.assignedcompany.name)
            temp_handles_sublist.append(temp_assigneddatadict)
            
            temp_assigneddatadict = {}
            temp_assigneddatadict["name"] = "User = "+str(handle.assigneduser.username)
            temp_handles_sublist.append(temp_assigneddatadict)
            
            temp_assigneddatadict = {}
            temp_assigneddatadict["name"] = "Checked? = "+str(handle.checked)
            temp_handles_sublist.append(temp_assigneddatadict)
            
            if temp_handles_sublist:
                temp_handles_subdict["children"] = temp_handles_sublist
            
            
            temp_assigneddatalist.append(temp_handles_subdict)
            
        if temp_assigneddatalist:
            temp_subdict["children"] = temp_assigneddatalist
        
        temp_sublist.append(temp_subdict)
        
        if temp_sublist:
            temp_dict["children"] = temp_sublist
        
        temp_list.append(temp_dict)
        
    if temp_list:
    
        main_dict["children"] = temp_list

    #print main_dict
    print entry_item
    
    transactions_dataset = main_dict
    
    searchtags = ['amount','doctype','date','account','memo','reftran','libelle','account']
    number_of_searchtags = len(searchtags)
   
    if number_of_searchtags>8:
        number_of_searchtags = 8
    
   
    context = {"the_user":the_user,'transactions_dataset':transactions_dataset,'entry_item':entry_item,
                'entry_item_pk':entry_item_pk,
                'entrylinks_pk':entrylinks_pk,'high_candidates_list':high_candidates_list,'medium_candidates_list':medium_candidates_list,
                'low_candidates_list':low_candidates_list,'excluded_candidates_list':excluded_candidates_list,'number_of_searchtags': number_of_searchtags,
                'searchtags':searchtags,}
    return render(request,'enersectapp/transaction_linking.html',context)