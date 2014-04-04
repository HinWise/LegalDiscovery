
from enersectapp.models import *

import json
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def transactions_report(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    the_user = request.user
   
    dataset = SourcePdf.objects.all()[10461:10468]
    
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
   
    json_posts = json.dumps(main_dict)
   
    context = {"the_user":the_user,'json_dataset':json_posts}
    return render(request,'enersectapp/transactions_report.html',context)