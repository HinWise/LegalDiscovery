
from enersectapp.models import *

import random

company_selected = Group.objects.get(name = "FlatWorld")

pdf_records_list = PdfRecord.objects.none()
pdf_records_list = PdfRecord.objects.all().values('ocrrecord_link','sourcedoc_link','sourcedoc_link__job_directory','sourcedoc_link__filename','id','audit_mark_saved','audit_mark_revision','EntryByCompany','AssignedLotNumber','EntryAuthor').order_by()
pdf_records_list = pdf_records_list.filter(EntryByCompany = company_selected).values('ocrrecord_link','sourcedoc_link','sourcedoc_link__job_directory','sourcedoc_link__filename','id','audit_mark_saved','audit_mark_revision','EntryByCompany','AssignedLotNumber','EntryAuthor').order_by()
pdf_records_list = pdf_records_list.filter(audit_mark_saved="save_audited_entry").distinct()
pdf_records_list = pdf_records_list.exclude(audit_mark = "auditmarked_confirmed_reassignment").exclude(audit_mark = "duplicatemarked_reentered")
pdf_records_list = pdf_records_list.filter(audit_mark_saved="save_audited_entry").distinct()
pdf_records_list = pdf_records_list.exclude(audit_mark_revision="auditmarked_as_correct").exclude(audit_mark_revision="auditmarked_as_incorrect").distinct()
pdf_records_list.count()
pdf_random_item = random.choice(pdf_records_list)
pdf_item_list = PdfRecord.objects.filter(id=pdf_random_item['id'])
pdf_item_list = pdf_item_list.order_by('-modification_date')
pdf_random_item