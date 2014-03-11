from django.db import connection
import time

def my_custom_sql(self):
    cursor = connection.cursor()
    
    firstTime = time.time()

    cursor.execute(self)

    lastTime = time.time() - firstTime

    print "THIS IS TIME ELAPSED ---> "+str(lastTime)
    return lastTime
    

totalTime = 0


a = 'SELECT DISTINCT "auth_user"."username" FROM "enersectapp_sourcepdftohandle" INNER JOIN "auth_user" ON ("enersectapp_sourcepdftohandle"."assigneduser_id" = "auth_user"."id") WHERE ("enersectapp_sourcepdftohandle"."assignedcompany_id" = 4 AND "enersectapp_sourcepdftohandle"."checked" = "checked" )'
my_custom_sql(a)

totalTime += my_custom_sql(a)
print "THIS IS TOTAL TIME SINCE FIRST QUERY ---> "+str(totalTime)