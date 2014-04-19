#This is the enersectapp urls file

from django.conf.urls import patterns, url

from enersectapp import views

urlpatterns = patterns('',

    # Maintenance Screen
    # ex: enersectapp/maintenance_screen
    url(r'^maintenance_screen/$', views.maintenance_screen, name='maintenance_screen'),

    # Note: To access to admin panel, the url is simply /admin
    # Admin already has an authentification mode built in.

    # Main (app_index). Shows the four available modes. Can't access them at the moment
    # ex: /enersectapp/
    url(r'^$', views.main_menu, name='main'),    
        
    # Link User Interface Main.
    # First screen a Link User encounters.
    # Saved for the future, auth purposes or an intro panel.
    # Actual Status: Redirects to Linking Cockpit (Spiderweb)
    # ex: /enersectapp/linkui
    url(r'^linkui/$', views.linkui, name='linkui'),
    
        # Link User Linking Cockpit (Spiderweb). (One Record, explore Pdf Records)
        # Screen with the panels and functions available to the Linking Users.
        # Right side contains the View Panel, that contains a Search By Attributes Search Box,
        # an Arbitrary Values Search, a PDF List, and PDF Visualizer
        # Left side contains the Records Panel, that contains a Search By Attributes Search Box,
        # an Arbitrary Values Search, a PDF List, and PDF Visualizer.
        # It also contains the actions
        # Actual Status: Redirects to Actions
        # ex: /enersectapp/linkui
        url(r'^linkui/spiderweb/$', views.linkui_spiderweb, name='linkui_spiderweb'),
    
    
        # Actual link action (One Record, explore Pdf Records)
        # Assigns the Primary Key of the Unlinked Record to the chosen PDF,
        # in the Foreign Key field.
        # It also changes the "status" of the record to Linked Record
        # Changes the linked_style_class of PdfRecord taken to ui-state-custom-linked (Green color)
        # Then it returns to Spiderweb
        # ex: /enersectapp/5/10/linkui_link
        url(r'^(?P<pdfrecord_id>\d+)/(?P<record_id>\d+)/linkui_link/$', views.linkui_link, name='linkui_link'),
        
        
        # Unlink action (One Record, explore Pdf Records)
        # The opposite of Link action,
        # Changes the error_style_class of the PdfRecord taken
        # to "nolink" (No color)
        
        # Then it returns to Spiderweb
        # ex: /enersectapp/5/linkui_unlink

        url(r'^(?P<pdfrecord_id>\d+)/linkui_unlink/$', views.linkui_unlink, name='linkui_unlink'),
        
        
        # Actual flag action (One Record, explore Pdf Records)
        # Changes the error_style_class of the PdfRecord taken
        # to ui-state-custom-error (Red color)
        # Changes the commentary of the PdfRecord taken
        # to contain "Error detected"
        # Then it returns to Spiderweb
        # ex: /enersectapp/5/10/linkui_link
        url(r'^linkui_flag/$', views.linkui_flag, name='linkui_flag'),
        
        
        # Unflag action (One Record, explore Pdf Records)
        # Changes the error_style_class of the PdfRecord taken
        # to "noerror" (No color)
         # Changes the commentary of the PdfRecord taken
        # to contain "Error solved"
        # Then it returns to Spiderweb
        # ex: /enersectapp/5/10/linkui_link
        url(r'^(?P<pdfrecord_id>\d+)/linkui_unflag/$', views.linkui_unflag, name='linkui_unflag'),
                
        # Skip action in Linking Interface (One Record, explore Pdf Records)
        # Skips the actual Record, putting it at the end of the list
        # ex: /enersectapp/2/skip
        url(r'^(?P<record_id>\d+)/linkui_skip/$', views.linkui_skip, name='linkui_skip'),
        
        
        #-------------------------------------------------------


        # Link User Linking Cockpit (Spiderweb). (One Pdf Record, explore Records)
        # Same as Spiderweb, but with Records in the place of PdfRecords and viceversa
        # ex: /enersectapp/linkui
        url(r'^linkui/spiderweb_viceversa/$', views.linkui_spiderweb_viceversa, name='linkui_spiderweb_viceversa'),
    
    
        # Actual link action (One Pdf Record, explore Records)
        # Same as Spiderweb, but with Records in the place of PdfRecords and viceversa
        # ex: /enersectapp/5/10/linkui_link
        url(r'^(?P<pdfrecord_id>\d+)/(?P<record_id>\d+)/linkui_link/viceversa$', views.linkui_link_viceversa, name='linkui_link_viceversa'),
        
        
        # Unlink action (One Pdf Record, explore Records)
        # Same as Spiderweb, but with Records in the place of PdfRecords and viceversa
        # ex: /enersectapp/5/linkui_unlink

        url(r'^(?P<record_id>\d+)/linkui_unlink/viceversa$', views.linkui_unlink_viceversa, name='linkui_unlink_viceversa'),
        
        
        # Actual flag action (One Pdf Record, explore Records)
        # Same as Spiderweb, but with Records in the place of PdfRecords and viceversa
        # ex: /enersectapp/5/10/linkui_link
        url(r'^linkui_flag/viceversa$', views.linkui_flag_viceversa, name='linkui_flag_viceversa'),
        
        
        # Unflag action (One Pdf Record, explore Records)
        # Same as Spiderweb, but with Records in the place of PdfRecords and viceversa
        # ex: /enersectapp/5/10/linkui_link
        url(r'^(?P<record_id>\d+)/linkui_unflag/viceversa$', views.linkui_unflag_viceversa, name='linkui_unflag_viceversa'),
               
        
        # Skip action in Linking Interface (One Pdf Record, explore Records)
        # Same as Spiderweb, but with Records in the place of PdfRecords and viceversa
        # ex: /enersectapp/2/skip
        url(r'^(?P<pdfrecord_id>\d+)/linkui_skip/viceversa$', views.linkui_skip_viceversa, name='linkui_skip_viceversa'),
        
        

    
        
    #Log In View when not authentificated
    #return redirect('/login/' % request.path)
    #ex: /enersectapp/login/
    url(r'^login/$', views.app_login, name='app_login'),
        
        
        
    # Data Entry Tool Main View, Spider
    # Displays a PDF and lets you choose what kind of Document that is
    # After that is chosen, it displays a form, with all the fields that must be
    # written down so the document is validly passed to the database.
    # A PDF List will be shown up from the server itself, or a chosen folder.
    # This is achieved programming it so it takes the links of those files.
    # When the Data is Submitted validly, it will create an OcrRecord with that
    # data, as well as a PdfRecord that will be linked to that Ocr.
    # It will save in a PdfRecord field that this data was introduced with this tool,
    # as well as the time in which it was created, and who did it.
    # ex: /enersectapp/dataentryui/spider
    url(r'^dataentryui/spider/$', views.dataentryui_spider, name='dataentryui_spider'),
    
        # Data Entry Tool, Save Data function
        # Saves an OcrRecord with the Data provided.
        # Option to pass the data through some filters and comprobations
        # before actually saving them in the database
        # ex: /enersectapp/dataentryui/spider
        url(r'^dataentryui_savedata/$', views.dataentryui_savedata, name='dataentryui_savedata'),
        
        
    # Auth Assign Source Pdfs for Data Entry Utility
        # For Superuser, assigns the selected Source Pdfs to a chosen Team (Company)
        # for Data Entry
        # Adds a SourcePdfToHandle to the field "assigndata" of the chosen Source Pdf's,
        # adding the name of the group/team to the assigned_company field.
        # ex: /admin/enersectapp/sourcepdf/sudo_assign
        url(r'^admin/enersectapp/sourcepdf/sudo_assign/$', views.sudo_assignsourcepdfsui, name='sudo_assignsourcepdfsui'),

    # Auth Assign Source Pdfs for Data Entry Utility
        # For Team Leaders, assigns the selected Source Pdfs to a chosen User in his Team (Company)
        # for Data Entry
        # Adds a SourcePdfToHandle to the field "assigndata" of the chosen Source Pdf's,
        # adding the name of the user to the assigneduser field.
        # ex: /admin/enersectapp/sourcepdf/lead_assign
        url(r'^admin/enersectapp/sourcepdf/lead_assign/$', views.lead_assignsourcepdfsui, name='lead_assignsourcepdfsui'),
        
        
    # Team Leader Interface
        # For Team Leaders, create Users, see the number of records assigned to your company
        # and assign them to different Users
        # When in "Round 2" of the Data Entry, documents will be assigned preferably to different users than
        # the one that made them the first time.
        
        # ex: /admin/enersectapp/teamleaderui/webcocoons
        url(r'^teamleaderui/webcocoons/$', views.webcocoons, name='webcocoons'),
    
        # Team Leader Interface
        # Save the assignations made in the Team Lead Interface
        # This view reorganizes those assignations respective to the number of
        # docs assigned. Will make it through filter()[:X] commands
        # ex: enersectapp/teamleaderui/webcocoons/cocoons_save
        url(r'^teamleaderui/webcocoons/cocoons_save/$', views.cocoons_save, name='cocoons_save'),

    # Team Leader Interface
        # 
        # ex: enersectapp/teamleaderui/webcocoons/cocoons_new_teamuser
        url(r'^teamleaderui/webcocoons/cocoons_new_teamuser/$', views.cocoons_new_teamuser, name='cocoons_new_teamuser'),
     
    
    # QA Spider Random Audit Interface
        # Interface to check if the data entry of random files from a lot was made correctly
        
        url(r'^auditui/randomqa_spider/$', views.randomqa_spider, name='randomqa_spider'), 
        
        
        
    # QA Pair Spider Random Audit Interface
        # Interface to check if the data entry of random files from a lot was made correctly. It audits pairs when available,
        # and has tools for building a third entry.
        
        url(r'^auditui/pair_randomqa_spider/$', views.pair_randomqa_spider, name='pair_randomqa_spider'), 
     
     
    # Categorization Tool Interface
    # Interface to check if the data entry of random files from a lot was made correctly
        
    url(r'^categoryui/document_type_categorization_tool/$', views.categorization_tool, name='categorization_tool'),

    # Blank or Not Blank Tool
    # Interface to check Blank Probables and pass them to either Blank or Other
        
    url(r'^categoryui/blank_or_not_blank/$', views.blank_or_not_blank, name='blank_or_not_blank'),
    
    # Auth Assign Source Pdfs for Data Entry Utility
    # For Superuser, chooses a Number of Random Source Pdfs to assign to one Team/Company,
    # as well as a Document Type to search from.
    # It should also tell how many of each Document Type are left to assign to that company
    # Adds a SourcePdfToHandle to the field "assigndata" of the chosen Source Pdf's,
    # adding the name of the group/team to the assignedcompany field, and the user "None" to
    # the assigneduser field.
    # ex: /admin/enersectapp/sourcepdf/sudo_assign_by_doctype_and_number
    url(r'^sourcepdf/sudo_assign_by_doctype_and_number/$', views.sudo_assignsourcepdfsui_by_doctype_and_number, name='sudo_assignsourcepdfsui_by_doctype_and_number'),
    
    # Progress Report
    # For Superuser,
    # Returns tables with the Fields:
    # Number of entries divided by Country
    # Number of each Doctype entered
    # Number of total documents entered
    # Number of total documents rejected
    # Number of total documents linked
    # Number of documents linked this week
    # Number of uncategorized remaining
    # See it by Vendor (Include which Company did what)
    # ex: enersectapp/reports/progress_report/
    url(r'^reports/progress_report/$', views.progress_report, name='progress_report'),
    
    # Category Changer Tool
    # ex: enersectapp/categoryui/category_changer/
    url(r'^categoryui/category_changer/$', views.category_changer, name='category_changer'),
    
    # Arabic Memo Edit Tool
    # ex: enersectapp/editui/arabic_memo_edit/
    url(r'^editui/arabic_memo_edit/$', views.arabic_memo_edit, name='arabic_memo_edit'),
    
    # Search Tool
    # Allows to search entries by multiple filters:
    # Company Name, Document Name, Amount, Date Range, Piece Number
    # ex: enersectapp/searchui/search_tool/
    url(r'^searchui/search_tool/$', views.search_tool, name='search_tool'),
   
    # Legal Discovery Tool
    # Allows to choose a Document Type, the extraction fields to include for them, and the sorting of them,
    # to be exported as a Legal Discovery Pdf Set
    # ex: enersectapp/legalui/legal_discovery/
    url(r'^legalui/legal_discovery/$', views.legal_discovery, name='legal_discovery'),
    
    # Transactions Report Tool
    # Allows to search for certain data in TransactionTable, Bank Records and Internal Records,
    # displays the relationships between those, and makes a formatted report about it in a pdf
    # ex: enersectapp/legalui/transactions_report/
    url(r'^legalui/transactions_report/$', views.transactions_report, name='transactions_report'),
   
   # Transaction Linking Tool
    # Allows to link PdfRecord table with TransactionTable elements,
    # as well as seeing the linked candidates and removing links
    # ex: enersectapp/linkui/transaction_linking/
    url(r'^linkui/transaction_linking/$', views.transaction_linking, name='transaction_linking'),
    
    # Show Transaction Tool
    # Allows to see a TransactionTable in a dendrogram.
    # Used for the iframe in Transaction Linking Tool
    # ex: /enersectapp/5/show_transaction

    url(r'^(?P<transaction_index>\d+)/show_transaction/$', views.show_transaction, name='show_transaction'),
    
    # Add or Remove Transaction from Candidate List
    # ex: /enersectapp/1230/14000/high/add/add_or_remove_transaction

    url(r'^(?P<entryId>\d+)/(?P<transactionId>\d+)/(?P<listType>\w+)/(?P<operationType>\w+)/add_or_remove_transaction/$', views.add_or_remove_transaction, name='add_or_remove_transaction'),
    
   
)
