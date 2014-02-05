
from enersectapp.models import *

from django.shortcuts import render

def app_index(request):
    
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    interface_type_list = UserInterfaceType.objects.all()
    the_user = request.user
   
    context = {'uitype_list':interface_type_list,"the_user":the_user}
    return render(request,'enersectapp/app_index.html',context)