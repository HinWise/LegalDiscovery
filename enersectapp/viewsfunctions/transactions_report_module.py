
from enersectapp.models import *
from django.db import transaction


from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def transactions_report(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    the_user = request.user
   
       
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

            if item["tag_name"] == "Unique PK":
            
                coincident_transactions = TransactionTable.objects.filter(pk = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('pk',flat=True))
            
            if item["tag_name"] == "Amount":
            
                coincident_transactions = TransactionTable.objects.filter(Amount__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('pk',flat=True))
            
            
            if item["tag_name"] == "NoPiece":
            
                print "NOPIECE" + item["tag_content"]
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('pk',flat=True))
            
    
            if item["tag_name"] == "Description":
            
                coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('pk',flat=True))

            if item["tag_name"] == "Company":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('pk',flat=True))
                
   
    coincident_transactions_dict = {}
   
    for item in coincident_transactions_list:
    
        coincident_transactions_dict[str(item)] = coincident_transactions_list.count(item)

    final_coincident_transactions_list = []
    
    for dict_key in coincident_transactions_dict.keys():
    
        temp_dict = {"pk":dict_key,"score":coincident_transactions_dict[dict_key]}
        final_coincident_transactions_list.append(temp_dict)

        
    final_list_ordered_score = []
    
    for score in range(number_of_searchtags,0,-1):
    
        temp_dict = {}
        temp_dict["transactions_list"] = [d for d in final_coincident_transactions_list if d['score'] == score]
        temp_dict["score_index"]= str(score);
        final_list_ordered_score.append(temp_dict)
    
    

    tag_types = ["Amount","NoPiece","Description","Company","Unique PK"]
    
    
    context = {"the_user":the_user,'number_of_searchtags': number_of_searchtags,
                'searchtags_string':searchtags_string,'final_list_ordered_score':final_list_ordered_score,"tag_types":tag_types,"searchtags":searchtags}
    return render(request,'enersectapp/transactions_report.html',context)