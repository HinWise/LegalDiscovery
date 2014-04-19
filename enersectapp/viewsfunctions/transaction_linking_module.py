
from enersectapp.models import *
from django.db import transaction

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
        selected_entry = request.POST['selected_entry']
    except:
        selected_entry = "none"
    
    try:
        
        if selected_entry !="none":
    
            entry_item = PdfRecord.objects.get(pk = selected_entry)

            
        entry_item_pk = entry_item.pk
        
        try:
        
            entrylinks_pk = entry_item.entrylinks_link.pk
            
            high_candidates_list = entry_item.entrylinks_link.high_candidates_list.all().order_by().values('pk')
            medium_candidates_list = entry_item.entrylinks_link.medium_candidates_list.all().order_by().values('pk')
            low_candidates_list = entry_item.entrylinks_link.low_candidates_list.all().order_by().values('pk')
            excluded_candidates_list = entry_item.entrylinks_link.excluded_candidates_list.all().order_by().values('pk')

        except:
        
            entrylinks_pk = 0
        
            high_candidates_list =[]
            medium_candidates_list = []
            low_candidates_list = []
            excluded_candidates_list = []
    
    except:
    
        corpus_entries = PdfRecord.objects.filter(entrylinks_link = None).order_by()

        corpus_entries_length = corpus_entries.count()

        entry_item_index = random.randint(0,corpus_entries_length)
        entry_item = corpus_entries[entry_item_index]
        entry_item_pk = entry_item.pk

        entrylinks_pk = 0
        high_candidates_list =[]
        medium_candidates_list = []
        low_candidates_list = []
        excluded_candidates_list = []
    

    #sample_transactions = TransactionTable.objects.all().order_by()[14698:14705]
    #sample_transactions = TransactionTable.objects.all().order_by()[14600:14607]
    
    #searchtags = ['amount','doctype','date','account','memo','reftran','libelle','account']
    
    searchtags = []
    
    #Example searchtags_string: "Amount:1000,Piece_Number:120"
    
    try:
        searchtags_string = request.POST['searchtags_string']
    except:
        searchtags_string = ""
    
    if searchtags_string:
    
        searchtags_fields = searchtags_string.split("+")
        
        for searchtag_fields in searchtags_fields:
        
            searchtag = searchtag_fields.split(":")
        
            searchtags_dict = {}
            searchtags_dict["tag_name"] = searchtag[0]
            searchtags_dict["tag_content"] = searchtag[1]
            searchtags.append(searchtags_dict)
            
    #print "THIS IS--->" + str(searchtags)
    
    number_of_searchtags = len(searchtags)
   
    if number_of_searchtags>8:
        number_of_searchtags = 8

        
    coincident_transactions = TransactionTable.objects.none()
    
    #Next Segment: Go throught the searchtags list-dictionary and search candidates in the corpus of entries following the chosen tags
    
    coincident_transactions_list = []
    
    with transaction.commit_on_success():
        for item in searchtags:
            
            if item["tag_name"] == "Unique Transaction Index":
            
                coincident_transactions = TransactionTable.objects.filter(TransactionIndex = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            if item["tag_name"] == "Amount":
            
                coincident_transactions = TransactionTable.objects.filter(Amount__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            
            if item["tag_name"] == "Piece Number":
            
                print "NOPIECE" + item["tag_content"]
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
    
            if item["tag_name"] == "Libdesc":
            
                coincident_transactions = TransactionTable.objects.filter(Libdesc__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))

            if item["tag_name"] == "Company":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            if item["tag_name"] == "Day":
            
                coincident_transactions = TransactionTable.objects.filter(PostDay = item["tag_content"]).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            if item["tag_name"] == "Month":
            
                coincident_transactions = TransactionTable.objects.filter(PostMonth = item["tag_content"]).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
   
            if item["tag_name"] == "Year":
            
                coincident_transactions = TransactionTable.objects.filter(PostYear = item["tag_content"]).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
   
            if item["tag_name"] == "Complete Date":
            
                divided_date = item["tag_content"].split("/")
            
                coincident_transactions = TransactionTable.objects.filter(PostDay = divided_date[0],PostMonth = divided_date[1],PostYear = divided_date[2] ).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay = divided_date[0],ValueMonth = divided_date[1],ValueYear = divided_date[2] ).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
   
   
            if item["tag_name"] == "Reftran":
            
                coincident_transactions = TransactionTable.objects.filter(Reftran = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Description":
            
                coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Bank Name":
            
                coincident_transactions = TransactionTable.objects.filter(BankName__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Bank Account":
            
                coincident_transactions = TransactionTable.objects.filter(BankAccount__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Bank Currency":
            
                coincident_transactions = TransactionTable.objects.filter(BankCurrency__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))

                
            if item["tag_name"] == "INT Account Number":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__AccountNum__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
                
            if item["tag_name"] == "Exchange Rate":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__ExchangeRate__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Memo":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
   
            if item["tag_name"] == "Movement Number":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
            
            if item["tag_name"] == "Lett":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True)) 
                
   
    coincident_transactions_dict = {}
   
    for item in coincident_transactions_list:
    
        coincident_transactions_dict[str(item)] = coincident_transactions_list.count(item)

    final_coincident_transactions_list = []
    
    for dict_key in coincident_transactions_dict.keys():
    
        temp_dict = {"TransactionIndex":dict_key,"score":coincident_transactions_dict[dict_key]}
        final_coincident_transactions_list.append(temp_dict)

        
    final_list_ordered_score = []
    
    for score in range(number_of_searchtags,0,-1):
    
        temp_dict = {}
        temp_dict["transactions_list"] = [d for d in final_coincident_transactions_list if d['score'] == score]
        temp_dict["score_index"]= str(score);
        final_list_ordered_score.append(temp_dict)
    
    

    tag_types = ["Amount","Piece Number","Company","Day","Month","Year","Complete Date","Libdesc","Description","Reftran",
    "Bank Name","Bank Account","Bank Currency","Unique Transaction Index","Movement Number","INT Account Number","Exchange Rate","Memo","Lett"]
    
    
    context = {"the_user":the_user,'entry_item':entry_item,
                'entry_item_pk':entry_item_pk,
                'entrylinks_pk':entrylinks_pk,'high_candidates_list':high_candidates_list,'medium_candidates_list':medium_candidates_list,
                'low_candidates_list':low_candidates_list,'excluded_candidates_list':excluded_candidates_list,'number_of_searchtags': number_of_searchtags,
                'searchtags_string':searchtags_string,'final_list_ordered_score':final_list_ordered_score,"tag_types":tag_types,"searchtags":searchtags}
    return render(request,'enersectapp/transaction_linking.html',context)