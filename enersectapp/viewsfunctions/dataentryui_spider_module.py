
from enersectapp.models import *
from enersectapp.viewsfunctions import common_functions_module

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response


def dataentryui_spider(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    #Mode indicates if the Pdfs to categorize are taken from the "No Category" Pool on the Source Pdfs, the "Other" Pool on the Entries, or All Entries.
    
    try:
        document_type = request.POST['doctype']
        
    except (KeyError):
    
        document_type='Document Type'
        
        
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
    
    types_list = {}
    
    if document_type == "Custom Generic Template":
    
        types_list = SourceDocType.objects.exclude(name="other").exclude(name="uncategorized").exclude(name="blank").exclude(name="recuperation").exclude(name="blank probable").order_by('name')
    
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
        
        all_from_user = SourcePdfToHandle.objects.filter(assigneduser = the_user)

        #count_assigned = sourcepdfs_list.count()
        count_assigned = all_from_user.count()
        
        #count_done = sourcepdfs_list.filter(assigndata__checked="checked",assigndata__assigneduser=the_user).count()
        #count_done = PdfRecord.objects.filter(EntryAuthor=the_user).values('sourcedoc_link').distinct().count()
        count_done = all_from_user.filter(checked = "checked").count()
        
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
    
    
    
    context = {'document_type':document_type,'companyname_list':companyname_list,
    'sourcepdfs_list':sourcepdfs_list,'the_user':the_user.username,'user_group':user_group.name,
    'count_assigned':count_assigned,'count_done':count_done,'types_list':types_list}
    return render(request,'enersectapp/dataentryui_spider.html',context)
    

def dataentryui_savedata(request):

    the_user = request.user

    try:
        doctype = request.POST['doctype']
    except:
        doctype = "NoDocTypeField"
   
    try:
        doctype2 = request.POST['doctype2']
    except:
        doctype2 = "NoDocType2Field"
   
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
    
    if len(company_address) == 0:
        company_address = "NoCompanyAddressField"
    
    try:
        company_telephone = request.POST['company_telephone']
    except:
        company_telephone = "NoCompanyTelephoneField"
    
    if len(company_telephone) == 0:
        company_telephone = "NoCompanyTelephoneField"
    
    try:
        company_city = request.POST['company_city']
    except:
        company_city = "NoCompanyCityField"
     
    if len(company_city) == 0:
        company_city = "NoCompanyCityField"
    
    try:
        company_country = request.POST['company_country']
    except:
        company_country = "NoCompanyCountryField"
    
    if len(company_country) == 0:
        company_country = "NoCompanyCountryField"
    
    try:
        company_template = request.POST['company_template']
    except:
        company_template = "NoCompanyTemplateField"
    
    if len(company_template) == 0:
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
        
    try:
        chequenum = request.POST['chequenum']
    except:
        chequenum = "NoChequeNumberField"
     
    try:
        receiver = request.POST['receiver']
    except:
        receiver = "NoReceiverField"
        
    try:
        sender = request.POST['sender']
    except:
        sender = "NoSenderField"
    
    new_pdf = common_functions_module.save_new_data_entry(doctype,doctype2,currency,amount,company_name,company_address,company_telephone,
    company_city,company_country,company_template,issuedate,issuedate_day,issuedate_month,issuedate_year,docnumber,
    memo,translation_memo,arabic,sourcedoc,file_name,purch_order_num,piece_number,receiver,sender,page_number,accountnum,chequenum,
    the_user)
    
    handles = new_pdf.sourcedoc_link.assigndata.filter(assigneduser=the_user)
  
    from django.db import transaction
  
    with transaction.commit_on_success():
        for handle in handles:
  
            try:
                lot_num = LotNumber.objects.get(lot_number = handle.lot_number)
            except:
                lot_num = LotNumber(lot_number = handle.lot_number)
        
            lot_num.save()
        
    new_pdf.AssignedLotNumber = lot_num
    new_pdf.save()
    
    
    return HttpResponseRedirect(reverse('enersectapp:dataentryui_spider', args=()))