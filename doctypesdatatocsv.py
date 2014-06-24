import csv
from enersectapp.models import *

b = open('doctypesinfo2.csv', 'w')
a = csv.writer(b)

data = []
all_types = SourceDocType.objects.all()

row = []
row.append("DocType Name")
row.append("Total Number Docs")
row.append("Total Assigned")
row.append("Total Assigned FlatWorld")
row.append("Total Done")
row.append("Total Not Done")
row.append("Total Assigned Enersect_Berlin")
row.append("Total Assigned NathanTeam")


data.append(row)

count = all_types.count()

for doctype in all_types:
    
    print count
    
    all_in_doctype = SourcePdf.objects.filter(modified_document_type = doctype)
    total_count = all_in_doctype.count()
    total_not_assigned = all_in_doctype.exclude(assigndata = None).count()
    total_assigned = total_count - total_not_assigned
    total_flatworld = all_in_doctype.filter(assigndata__assignedcompany__name = "FlatWorld").count()
    total_enerberlin = all_in_doctype.filter(assigndata__assignedcompany__name = "Enersect_Berlin").count()
    total_nathanteam = all_in_doctype.filter(assigndata__assignedcompany__name = "NathanTeam").count()
    all_done = all_in_doctype.filter(assigndata__checked = "checked").distinct()
    total_done = all_done.count()
    total_not_done = total_count - total_done
    
    row = []
    row.append(doctype.name)
    row.append(str(total_count))
    row.append(str(total_assigned))
    row.append(str(total_flatworld))
    row.append(str(total_done))
    row.append(str(total_not_done))
    row.append(str(total_enerberlin))
    row.append(str(total_nathanteam))
    data.append(row)
    count = count - 1
    

a.writerows(data)
b.close()