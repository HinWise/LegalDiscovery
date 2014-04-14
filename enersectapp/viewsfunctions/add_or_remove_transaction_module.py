
from enersectapp.models import *

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def add_or_remove_transaction(request,entryId,transactionId,listType,operationType):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))

    the_user = request.user

    entry_item = PdfRecord.objects.get(pk = entryId)
    transaction_item = TransactionTable.objects.get(pk=transactionId)

    print "THIS IS PK -->"+str(entry_item.pk)
    
    try:
        entry_links_table = entry_item.entrylinks_link
        test_var = entry_links_table.entry_pk

    except:
        entry_links_table = EntryLinks(entry_pk=entry_item.pk)
        entry_links_table.save()
        entry_item.entrylinks_link = entry_links_table
        entry_item.save()

    
    if listType == "exclude":
    
        
        if operationType == "add":

            entry_links_table.excluded_candidates_list.add(transaction_item)
    
        if operationType == "remove":

            entry_links_table.excluded_candidates_list.remove(transaction_item)
    
    elif listType == "low":

        if operationType == "add":

            entry_links_table.low_candidates_list.add(transaction_item)
    
        if operationType == "remove":

            entry_links_table.low_candidates_list.remove(transaction_item)
    
    elif listType =="medium":

        if operationType == "add":

            entry_links_table.medium_candidates_list.add(transaction_item)
        
        if operationType == "remove":

            entry_links_table.medium_candidates_list.remove(transaction_item)
        
    elif listType == "high":

        if operationType == "add":
        
            entry_links_table.high_candidates_list.add(transaction_item)
            
        if operationType == "remove":

            entry_links_table.high_candidates_list.remove(transaction_item)

    print "FINISHED"
   
    return HttpResponse("Added/deleted transaction succesfully")
