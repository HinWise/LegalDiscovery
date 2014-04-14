
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


    
            
    report_type = "transaction_linking"
    report_subtype = operationType+"_operation"
    report_memo = "Transaction with PK."+str(transaction_item.pk)+". affected by operation ."+operationType+". from/to list ."+listType+". in entry PdfRecord with PK."+str(entry_item.pk)+"."
    report_author = the_user
    report_company = the_user.groups.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]

    new_report = Report(report_type = report_type,report_subtype=report_subtype,report_memo=report_memo,report_author=report_author,report_company=report_company)

    new_report.save()
   
    return HttpResponse("Added/deleted transaction succesfully")
