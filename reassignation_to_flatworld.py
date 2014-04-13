
from enersectapp.models import *
from django.db import transaction

flatworld = Group.objects.get(name="FlatWorld")

#Turn variations of Missing in Company Names, Piece Numbers o Document Numbers to "MISSING", and of unreadable to "UNREADABLE"

all_miscompany = OcrRecord.objects.filter(Company__icontains = "issin")

with transaction.commit_on_success():
    for item in all_miscompany:
        item.Company = "MISSING NAME"
        item.save()
  
all_unrecompany = OcrRecord.objects.filter(Company__icontains = "reada")

with transaction.commit_on_success():
    for item in all_unrecompany:
        item.Company = "UNREADABLE NAME"
        item.save()
  
all_mispiece = OcrRecord.objects.filter(Piece_Number__icontains = "issin")

with transaction.commit_on_success():
    for item in all_mispiece:
        item.Piece_Number = "MISSING"
        item.save()
  
all_unrepiece = OcrRecord.objects.filter(Piece_Number__icontains = "reada")

with transaction.commit_on_success():
    for item in all_unrepiece:
        item.Piece_Number = "UNREADABLE"
        item.save()
  
all_misdocnum = OcrRecord.objects.filter(Document_Number__icontains = "issin")

with transaction.commit_on_success():
    for item in all_misdocnum:
        item.Document_Number = "MISSING"
        item.save()
  
all_unredocnum = OcrRecord.objects.filter(Document_Number__icontains = "reada")

with transaction.commit_on_success():
    for item in all_unredocnum:
        item.Document_Number = "UNREADABLE"
        item.save()
  

base_set = PdfRecord.objects.exclude(AssignedLotNumber__lot_number = 31).filter(audit_mark_saved = "save_audited_entry")

missing_lot_list = [6,8,9,10,1,12,13,14,18,19,21,22,24,25,27,32,33,35,36,37]

missing_piece_number = [8,9,10,12,13,18,22]

total_missing = base_set.filter(ocrrecord_link__Amount = "MISSING") | base_set.filter(ocrrecord_link__Day = "NaN") | base_set.filter(ocrrecord_link__Month = "NaN") | base_set.filter(ocrrecord_link__Year = "NaN") | base_set.filter(ocrrecord_link__Company = "MISSING NAME") | base_set.filter(ocrrecord_link__Company = "UNREADABLE NAME") | base_set.filter(ocrrecord_link__Document_Type = "Other") | base_set.filter(ocrrecord_link__Document_Type = "Blank")

with transaction.commit_on_success():
    for lot_num in missing_piece_number:
       
        total_missing = total_missing | base_set.filter(AssignedLotNumber__lot_number = lot_num,ocrrecord_link__Piece_Number = "MISSING") | base_set.filter(AssignedLotNumber__lot_number = lot_num,ocrrecord_link__Piece_Number = "UNREADABLE")

        
with transaction.commit_on_success():
    for item in total_missing:
        item.audit_mark_saved = "awaiting_audit"
        item.save()

#0,1,2,3,4,5,7,15,20,23,26,28,30,34,38
complete_lot_list = [0,1,2,3,4,5,7,15,20,23,26,28,30,34,38]

with transaction.commit_on_success():
 for lot_num in complete_lot_list:
    selected_by_lot = base_set.filter(AssignedLotNumber__lot_number = lot_num)
    print lot_num
    for item in selected_by_lot:
        item.audit_mark_saved = "awaiting_audit"
        item.save()

