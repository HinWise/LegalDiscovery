
from enersectapp.models import *
from enersectapp.viewsfunctions import common_functions_module

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def sudo_assignsourcepdfsui(request):
        
        
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        sourcepdf_list = request.POST['sourcepdfs_list']
        
    except (KeyError):
    
        sourcepdf_list ='SourcePdf List Empty'
    
    try:
        the_user_name = request.POST['the_user']
        
    except (KeyError):
    
        the_user_name ='User Name Empty'
        
    try:
        user_group_name = request.POST['user_group']
        
    except (KeyError):
    
        user_group_name ='User Group Name Empty'
          
    try:
        company_name = request.POST['company_name']
        
    except (KeyError):
    
        company_name ='Company To Assign Empty'
    
    #print sourcepdf_list,the_user,company_name,user_group
    
    sourcepdf_list = str(sourcepdf_list)
    sourcepdf_list = sourcepdf_list.split('|');
    sourcepdf_list = sourcepdf_list[:-1]
    
    controluser = User.objects.get(username="None")
    assigned_group = Group.objects.get(name=company_name)
    
    with transaction.commit_on_success():
        for item in sourcepdf_list:
            if item:
                #the_user.assignedsourcepdfs.add(source)
                
                source = SourcePdf.objects.get(id=int(item))
                
                if source.assigndata.exclude(assignedcompany__name=company_name):
                    tohandle = SourcePdfToHandle(assignedcompany=assigned_group,assigneduser=controluser)
                    tohandle.save()
                    source.assigndata.add(tohandle)
                    source.save()
                    #the_user.save()
                
    return redirect('/admin/enersectapp/sourcepdf')
    
def lead_assignsourcepdfsui(request):
       
        
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        sourcepdf_list = request.POST['sourcepdfs_list']
        
    except (KeyError):
    
        sourcepdf_list ='SourcePdf List Empty'

    try:
        the_user = request.POST['the_user']
        
    except (KeyError):
    
        the_user ='User Empty'
          
    try:
        user_name = request.POST['user_name']
        
    except (KeyError):
    
        user_name ='User To Assign Empty'
        
    try:
        user_group_name = request.POST['user_group']
        
    except (KeyError):
    
        user_group_name ='User Group assigned Empty'
    
    #print sourcepdf_list,the_user,company_name
    
    sourcepdf_list = str(sourcepdf_list)
    sourcepdf_list = sourcepdf_list.split('|');
    sourcepdf_list = sourcepdf_list[:-1]
    
    the_user = User.objects.filter(username=user_name)[0]
    
    with transaction.commit_on_success():
        for item in sourcepdf_list:
            if item:
                source = SourcePdf.objects.get(id=int(item))
                
                #the_user.assignedsourcepdfs.add(source)
                handles = source.assigndata.all().filter(assignedcompany__name = user_group_name).exclude(assigneduser__username = user_name)
                for handle in handles:
                   
                    if handle:
                        handle.assigneduser = the_user
                        handle.save()
                        source.save()
                        #the_user.save()
    
    return redirect('/admin/enersectapp/sourcepdf')  