import csv
from enersectapp.models import *

b = open('doctypesinfo.csv', 'w')
a = csv.writer(b)

data = []
all_types = SourceDocType.objects.all()

for doctype in all_types:
    
    all_in_doctype = SourcePdf.objects.filter(modified_document_type = doctype)
    total_count = all_in_doctype.count()
    total_not_assigned = all_in_doctype.filter(assigndata = None).count()
    total_assigned = total_count - total_not_assigned
    total_flatworld = all_in_doctype.filter(assigndata__assignedcompany__name = "FlatWorld").count()
    total_enerberlin = all_in_doctype.filter(assigndata__assignedcompany__name = "Enersect_Berlin").count()
    total_nathanteam = all_in_doctype.filter(assigndata__assignedcompany__name = "NathanTeam").count()
    
    row = []
    row.append(doctype.name)
    row.append(str(total_count))
    row.append(str(total_assigned))
    row.append(str(total_flatworld))
    row.append(str(total_enerberlin))
    row.append(str(total_nathanteam))
    
    
    data.append(row)
    

a.writerows(data)
b.close()