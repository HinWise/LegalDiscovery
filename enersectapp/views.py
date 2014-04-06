from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate

from django.shortcuts import get_object_or_404, render, redirect,render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template import RequestContext
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime
from django.db import transaction
from django.db import connection
import re
import json,csv
from django.core import serializers
import random
from pyPdf import PdfFileWriter, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO
from django.db.models import Count

from enersectapp.viewsfunctions import (app_index_module,app_login_module,linkui_spiderweb_module,linkui_spiderweb_viceversa_module,dataentryui_spider_module,
                                        pair_randomqa_spider_module,assign_source_pdfs_module,webcocoons_module,randomqa_spider_module,categorization_tool_module,
                                        blank_or_not_blank_module,sudo_assignsourcepdfsui_by_module,progress_report_module,category_changer_module,
                                        arabic_memo_edit_module,search_tool_module,legal_discovery_module,transactions_report_module,transaction_linking_module,
                                        show_transaction_module)

from enersectapp.models import *


def maintenance_screen(request):
  
    return render(request,'enersectapp/maintenance_screen.html',context)

def app_login(request):
  
    return app_login_module.app_login(request)

def main_menu(request):
    
    return app_index_module.app_index(request)

     
def linkui(request):
    return linkui_spiderweb_module.linkui(request)

 
def linkui_spiderweb(request):
    
    return linkui_spiderweb_module.linkui_spiderweb(request)
    
    
def linkui_link(request, pdfrecord_id, record_id):
    
    return linkui_spiderweb_module.linkui_link(request, pdfrecord_id, record_id)


def linkui_unlink(request, pdfrecord_id):
    
    return linkui_spiderweb_module.linkui_unlink(request, pdfrecord_id)
    
def linkui_flag(request):
    
    return linkui_spiderweb_module.linkui_flag(request)   
    
def linkui_unflag(request, pdfrecord_id):
    
    return linkui_spiderweb_module.linkui_unflag(request, pdfrecord_id)   


def linkui_skip(request, record_id):
    
    return linkui_spiderweb_module.linkui_skip(request, record_id)
    

#####---Starts the Linkui view for "Viceversa", when an unlinked Pdf Record is called and multiple Records
# are dynamic

def linkui_spiderweb_viceversa(request):
    
    return linkui_spiderweb_viceversa_module.linkui_spiderweb_viceversa(request)
    
def linkui_link_viceversa(request, pdfrecord_id, record_id):
    
    return linkui_spiderweb_viceversa_module.linkui_link_viceversa(request, pdfrecord_id, record_id)


def linkui_unlink_viceversa(request, record_id):
    
    return linkui_spiderweb_viceversa_module.linkui_unlink_viceversa(request, record_id)  
    
def linkui_flag_viceversa(request):
    
    return linkui_spiderweb_viceversa_module.linkui_flag_viceversa(request)  
    
def linkui_unflag_viceversa(request, record_id):
    
    return linkui_spiderweb_viceversa_module.linkui_unflag_viceversa(request, record_id)      


def linkui_skip_viceversa(request, pdfrecord_id):
    
    return linkui_spiderweb_viceversa_module.linkui_skip_viceversa(request, pdfrecord_id)


def dataentryui_spider(request):
    
    return dataentryui_spider_module.dataentryui_spider(request)

    
def dataentryui_savedata(request):

    return dataentryui_spider_module.dataentryui_savedata(request)


def webcocoons(request):

    return webcocoons_module.webcocoons(request)
    
def cocoons_save(request):

    return webcocoons_module.cocoons_save(request)
    
    
def cocoons_new_teamuser(request):

    return webcocoons_module.cocoons_new_teamuser(request)

def randomqa_spider(request):

    return randomqa_spider_module.randomqa_spider(request)

def pair_randomqa_spider(request):

    return pair_randomqa_spider_module.pair_randomqa_spider(request)
        

def categorization_tool(request):
    
    
    return categorization_tool_module.categorization_tool(request)

    
def blank_or_not_blank(request):

    return blank_or_not_blank_module.blank_or_not_blank(request)

    
def sudo_assignsourcepdfsui_by_doctype_and_number(request):
       
    return sudo_assignsourcepdfsui_by_module.sudo_assignsourcepdfsui_by_doctype_and_number(request)


def progress_report(request):

    return progress_report_module.progress_report(request)

def category_changer(request):

    return category_changer_module.category_changer(request)
    

def arabic_memo_edit(request):
    
    return arabic_memo_edit_module.arabic_memo_edit(request)
    
def search_tool(request):
    
    return search_tool_module.search_tool(request)
    
def legal_discovery(request):
    
    return legal_discovery_module.legal_discovery(request)
    
def transactions_report(request):
    
    return transactions_report_module.transactions_report(request)

def transaction_linking(request):
    
    return transaction_linking_module.transaction_linking(request)    
    
def show_transaction(request,transaction_pk):
    
    return show_transaction_module.show_transaction(request,transaction_pk)  
  


###DEPRECATED FUNCTIONS, STILL IN THE SYSTEM THOUGH (WHEN ACCESSING TO THE ASSIGN BUTTON IN THE ADMIN)
  
    
def sudo_assignsourcepdfsui(request):
        
    return assign_source_pdfs_module.sudo_assignsourcepdfsui(request)
    
def lead_assignsourcepdfsui(request):
     
    return assign_source_pdfs_module.lead_assignsourcepdfsui(request)
    
###       