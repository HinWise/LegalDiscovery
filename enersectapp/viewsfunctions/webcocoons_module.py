
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection

from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def webcocoons(request):

    the_user = request.user

    if not the_user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic").exclude(name="Arabic")[0]
    noneuser = User.objects.get(username="None")
    
    
    if the_user.groups.filter(name="TeamLeaders").exists():
        
        sourcepdfs_list = ""
       
        sourcepdfs_list = SourcePdfToHandle.objects.filter(assignedcompany=user_group).order_by()
                
        count_total = len(sourcepdfs_list)
        
        sourcepdfs_notassigned = SourcePdfToHandle.objects.filter(assigneduser=noneuser).order_by()
        sourcepdfs_notcomplete = SourcePdfToHandle.objects.filter(assignedcompany=user_group,checked="unchecked").order_by()
        
        count_notassigned = len(sourcepdfs_notassigned)
        count_notcomplete = len(sourcepdfs_notcomplete)
        count_assigned = count_total - count_notassigned
        
        count_done = count_total - count_notcomplete
        #count_done = sourcepdfs_list.filter(checked="checked").count()
               
        all_users_from_group_not_myself = User.objects.filter(groups=user_group).exclude(username=the_user.username)
       
        user_dictionary_values_list = []
        
        user_dictionary = { "name":"","assigned_count":0,"user_checked_count":0}
        
        count_total_categorizations = 0
        count_total_blank_or_not_blank = 0
                
        for index, item in enumerate(all_users_from_group_not_myself):
            user_dictionary = {}
            user_dictionary.update({"name":item.username})
            assigned_pdfs = SourcePdfToHandle.objects.filter(assigneduser=item)
            checked_count = assigned_pdfs.filter(checked="checked").count()
            assigned_unchecked_count = assigned_pdfs.exclude(checked="checked").count()
            user_profile = UserProfile.objects.get(user = item)
            completed_categorizations = len(user_profile.modifiedsourcepdfs_categorization_tool.all())+ len(user_profile.modifiedpdfs_categorization_tool.all())
            completed_blank_or_not_blank = len(user_profile.modifiedsourcepdfs_blank_or_not_tool.all())
            assignation_locked = user_profile.assignation_locked
            
            count_total_categorizations = count_total_categorizations+completed_categorizations
            count_total_blank_or_not_blank = count_total_blank_or_not_blank+completed_blank_or_not_blank
            
            user_dictionary.update({"assigned_unchecked_count":assigned_unchecked_count})
            
            user_dictionary.update({"checked_count":checked_count})
            
            user_dictionary.update({"id":item.id})
            
            user_dictionary.update({"completed_categorizations":completed_categorizations})
            
            user_dictionary.update({"completed_blank_or_not_blank":completed_blank_or_not_blank})
            
            user_dictionary.update({"assignation_locked":assignation_locked})
            
            user_dictionary_values_list.append(user_dictionary)
            
        
       
        context = {'user_dictionary_values_list':user_dictionary_values_list,
        'the_user':the_user.username,'user_group':user_group.name,
        'count_assigned':count_assigned,'count_done':count_done,'count_total':count_total,
        'count_notassigned':count_notassigned,'count_notcomplete':count_notcomplete,
        'count_total_categorizations':count_total_categorizations,'count_total_blank_or_not_blank':count_total_blank_or_not_blank}
        return render(request,'enersectapp/webcocoons.html',context)
       
    else:
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
       
    
@transaction.commit_manually    
def cocoons_save(request):

    try:
    
        the_user = request.user

        if not the_user.is_authenticated():
        
            return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    
        user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
    
        sourcepdfstohandle_list = SourcePdfToHandle.objects.filter(assignedcompany=user_group).exclude(checked="checked")
    
        #count_before_exclusion = len(sourcepdfstohandle_list)
        
        all_users_from_group_not_myself = User.objects.filter(groups=user_group).exclude(username=the_user.username)

        none_user = User.objects.get(username="None")
    
        count = 0
    
        
        #Locks and Unlocks users, in agreement what has been sent in TeamLeader's Interface
        print str(len(all_users_from_group_not_myself))+"--THIS IS LEN"
        for item in all_users_from_group_not_myself:
                        
            locked = request.POST['assignation_locked|'+item.username]
            user_profile = UserProfile.objects.get(user = item)
                        
            if user_profile.assignation_locked != locked:
            
                if locked == "locked":
                    user_profile.assignation_locked = "locked"
                else:
                    user_profile.assignation_locked = "not_locked"
                    
                    
                user_profile.save()
                
        
        #Resetting all the unassigned files to User None before making the real assignment
        #This ensures that you can actually delete an assignation without assigning to another user
    
        #Edit: Will only update the ones whose User is not locked. This is what the next for-loop is for.
        
        all_locked_userprofiles_company = UserProfile.objects.filter(user_company = user_group,assignation_locked = "locked")
        
        for user_profile in all_locked_userprofiles_company:
        
            sourcepdfstohandle_list = sourcepdfstohandle_list.exclude(assigneduser = user_profile.user)
    
        #count_after_exclusion = len(sourcepdfstohandle_list)
    
        #count_difference = count_before_exclusion-count_after_exclusion
    
        for item in sourcepdfstohandle_list:
            item.assigneduser = none_user
            item.save()
    
    
     
        #Real assignation. It starts with the assigning the appropriate number of documents to the first user
        #and proceeds from there on.
    
        for item in all_users_from_group_not_myself:
            
            is_user_locked = all_locked_userprofiles_company.filter(user=item)
            
            if len(is_user_locked) == 0:
            
                maxNum = request.POST['name|'+item.username]
                maxNum = int(maxNum)
                temp_list = sourcepdfstohandle_list[count:count+maxNum]
                count = count + maxNum
                for to_assign in temp_list:
                    to_assign.assigneduser = item
                    to_assign.save()
    
    
        retval = HttpResponseRedirect(reverse('enersectapp:main', args=()))

        transaction.commit()
        return retval
        
    except:
        
        retval = HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
        transaction.rollback()
        return retval
    
        

def cocoons_new_teamuser(request):

    the_user = request.user;
    
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]

    if request.POST:
        username = request.POST['username']
        
        password = request.POST['password'].encode('ascii','replace')
        repeat_password = request.POST['repeat_password'].encode('ascii','replace')

        if password == repeat_password:
        
            user = User.objects.create_user(username, password)
            user.username = username
            user.set_password(repeat_password)
            user.groups.add(user_group)
            user.is_staff = True
            user.is_active = True
            user.save()
            
            user_profile = UserProfile.objects.get(user = user)
            user_profile.user_company = user_group
            user_profile.save()
        
            return HttpResponseRedirect(reverse('enersectapp:webcocoons', args=()))
        else:
            return HttpResponseRedirect(reverse('enersectapp:main', args=()))