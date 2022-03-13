from django.shortcuts import render
from django.core.paginator import Paginator
import logging

from ecs.core.models.core import MedicalCategory

# @user_group_required('EC-Office', 'EC-Executive')
def index(request):
    limit = 20
    page = request.GET.get('page', 1)

    medical_category_list = MedicalCategory.objects.distinct()
    paginator = Paginator(medical_category_list, limit, allow_empty_first_page=True)
    try:
        medical_category = paginator.page(page)
    except:
        medical_category = paginator.page(1)
    
    return render(request, 'medical_category/base.html', {
        'medical_category': medical_category
    })