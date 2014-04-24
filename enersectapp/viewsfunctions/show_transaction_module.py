
from enersectapp.models import *

import json
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def show_transaction(request,transaction_index):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    the_user = request.user
   
  
    transaction_item = TransactionTable.objects.get(TransactionIndex=transaction_index)
    
    
    item_bank_records = transaction_item.bank_records_list.all()
    
    bank_records_list = []
    
    
    for bank_record in item_bank_records:
    
        helper_dict = {"name":"Bank Record "+ str(bank_record.BankRecordIndex),"children":[
            {"name":"Amount = "+str(bank_record.Amount)},
            {"name":"PostDate = "+bank_record.PostDay+"/"+bank_record.PostMonth+"/"+bank_record.PostYear},
            {"name":"ValueDate = "+bank_record.ValueDay+"/"+bank_record.ValueMonth+"/"+bank_record.ValueYear},
            {"name":"Libdesc = "+bank_record.Libdesc},
            {"name":"Reftran = "+bank_record.Reftran},
            {"name":"Libelle = "+bank_record.Libelle},
            {"name":"Reference = "+bank_record.Reference},
            {"name":"BankName = "+bank_record.BankName},
            {"name":"BankAccount = "+bank_record.BankAccount},
            {"name":"BankCurrency = "+bank_record.BankCurrency},
            {"name":"Description = "+str(bank_record.Description)},
            {"name":"Provenance = "+str(bank_record.Provenance)},
            
        ]}
        bank_records_list.append(helper_dict)

    
    item_internal_records = transaction_item.internal_records_list.all()
    
    internal_records_list = []
    
    for internal_record in item_internal_records:
    
        helper_dict = {"name":"Internal Record "+ str(internal_record.InternalRecordIndex),"children":[
            {"name":"Credit = "+str(internal_record.Credit) + " Dinars"},
            {"name":"Debit = "+str(internal_record.Debit) + " Dinars"},
            {"name":"Complete Date = "+internal_record.Day+"/"+internal_record.Month+"/"+internal_record.Year},
            {"name":"DateDiscrepancy = "+str(internal_record.DateDiscrepancy)},
            {"name":"LedgerYear = "+internal_record.LedgerYear},
            {"name":"Company = "+internal_record.Company},
            {"name":"Lett = "+internal_record.Lett},
            {"name":"AccountNum = "+internal_record.AccountNum},
            {"name":"BankName = "+internal_record.BankName},
            {"name":"BankAccount = "+internal_record.BankAccount},
            {"name":"BankCurrency = "+internal_record.BankCurrency},
            {"name":"ExistingBankEntry = "+str(internal_record.ExistingBankEntry)},
            {"name":"ExchangeRate = "+str(internal_record.ExchangeRate)},
            {"name":"NoMvt = "+str(internal_record.NoMvt)},
            {"name":"Journal = "+str(internal_record.Journal)},
            {"name":"NoPiece = "+str(internal_record.NoPiece)},
            {"name":"S = "+str(internal_record.S)},
            {"name":"Memo = "+str(internal_record.Memo)},
            {"name":"MEDollars = "+str(internal_record.MEDollars)},
            {"name":"MEPounds = "+str(internal_record.MEPounds)},
            {"name":"MEEuros = "+str(internal_record.MEEuros)},
            {"name":"MEChequeNum = "+str(internal_record.MEChequeNum)},
            {"name":"MECategory = "+str(internal_record.MECategory)},
            {"name":"MEDate = "+str(internal_record.MEDate)},
            {"name":"MECutoff = "+str(internal_record.MECutoff)},
            {"name":"MEFactureNum = "+str(internal_record.MEFactureNum)},
            
            
        ]}
        internal_records_list.append(helper_dict)

    if len(internal_records_list) > 0:
        internal_records_dict = {"name":"Associated Internal Records","children":internal_records_list}
    else:
        internal_records_dict = {"name":"Associated Internal Records"}
        
    if len(bank_records_list) > 0:
        bank_records_dict = {"name":"Associated Bank Records","children":bank_records_list}
    else:
        bank_records_dict = {"name":"Associated Bank Records"}
        
    main_content_list = [{"name":"Amount = "+transaction_item.Amount},{"name":"Amount Discrepancy= "+str(transaction_item.AmountDiscrepancy)},
        {"name":"PostDate = "+transaction_item.PostDay+"/"+transaction_item.PostMonth+"/"+transaction_item.PostYear},
        {"name":"ValueDate = "+transaction_item.ValueDay+"/"+transaction_item.ValueMonth+"/"+transaction_item.ValueYear},
        {"name":"DateDiscrepancy = "+str(transaction_item.DateDiscrepancy)},
        {"name":"Libdesc = "+transaction_item.Libdesc},
        {"name":"Reftran = "+transaction_item.Reftran},
        {"name":"BankName = "+transaction_item.BankName},
        {"name":"BankAccount = "+transaction_item.BankAccount},
        {"name":"BankCurrency = "+transaction_item.BankCurrency},
        {"name":"NumberBankRecordIndexes = "+str(transaction_item.NumberBankRecordIndexes)},
        bank_records_dict,
        {"name":"NumberInternalRecordIndexes = "+str(transaction_item.NumberInternalRecordIndexes)},
        internal_records_dict
    ]
    
    transaction_dict = { "name":"Transaction "+str(transaction_item.TransactionIndex),"children":main_content_list}
 
    transaction_dict = json.dumps(transaction_dict)

    #print main_dict
   
    #json_posts = json.dumps(main_dict)
   
    context = {"the_user":the_user,'transaction_dict':transaction_dict}
    return render(request,'enersectapp/show_transaction.html',context)