from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ecs.core.models.core import MedicalCategory
from ecs.core.models.medical_category import MedicalCategoryCreationForm

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

def create_medical_category(request):
    form = MedicalCategoryCreationForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        name = form.data.get('name')
        abbrev = form.data.get('abbrev')
        MedicalCategory.objects.create(name=name, abbrev=abbrev)
        return redirect('ecs.core.views.medical_category.index')

    return render(request, 'medical_category/create.html', {
        'form': form
    })

def update_medical_category(request, pk):
    if request.method == 'POST' and request.POST:
        form = MedicalCategoryCreationForm(request.POST)
        if form.is_valid():
            name = form.data.get('name')
            abbrev = form.data.get('abbrev')
            MedicalCategory.objects.filter(id=pk).update(name=name, abbrev=abbrev)
            return redirect('ecs.core.views.medical_category.index')
    else:
        medical_category = MedicalCategory.objects.filter(id=pk).first()
        form = MedicalCategoryCreationForm({
            "name": medical_category.name,
            "abbrev": medical_category.abbrev
        })

    return render(request, 'medical_category/update.html', {
        'form': form
    })