from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ecs.core.models.core import MedicalCategory
from ecs.core.models.medical_category import MedicalCategoryCreationForm
from ecs.users.utils import user_group_required

@user_group_required('EC-Executive')
def administration(request):
    limit = 20
    page = request.GET.get('page', 1)

    medical_category_list = MedicalCategory.objects.all().order_by('is_disabled', 'name')
    paginator = Paginator(medical_category_list, limit, allow_empty_first_page=True)
    try:
        medical_category = paginator.page(page)
    except:
        medical_category = paginator.page(1)
    
    return render(request, 'medical_category/base.html', {
        'medical_category': medical_category
    })

@user_group_required('EC-Executive')
def create_medical_category(request):
    form = MedicalCategoryCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        name = form.data.get('name')
        abbrev = form.data.get('abbrev')
        isAbbrevUnique = MedicalCategory.objects.filter(abbrev=abbrev).first() is None
        if isAbbrevUnique:
            MedicalCategory.objects.create(name=name, abbrev=abbrev)
            return redirect('ecs.core.views.medical_category.administration')
        else:
            return render(request, 'medical_category/create.html', {
                'form': form
            })

    return render(request, 'medical_category/create.html', {
        'form': form
    })

@user_group_required('EC-Executive')
def update_medical_category(request, pk):
    if request.method == 'POST' and request.POST:
        form = MedicalCategoryCreationForm(request.POST or None)
        if form.is_valid():
            name = form.data.get('name')
            abbrev = form.data.get('abbrev')
            medical_category = MedicalCategory.objects.filter(id=pk).first()
            isAbbrevUnique = medical_category.abbrev == abbrev or MedicalCategory.objects.filter(abbrev=abbrev).first() is None
            if isAbbrevUnique:
                MedicalCategory.objects.filter(id=pk).update(name=name, abbrev=abbrev)
                return redirect('ecs.core.views.medical_category.administration')
    else:
        medical_category = MedicalCategory.objects.filter(id=pk).first()
        form = MedicalCategoryCreationForm({
            "name": medical_category.name,
            "abbrev": medical_category.abbrev
        })

    return render(request, 'medical_category/update.html', {
        'form': form
    })

@user_group_required('EC-Executive')
def toggle_disabled(request, pk):
    medical_category = MedicalCategory.objects.filter(id=pk).first()
    if medical_category is not None:
        MedicalCategory.objects.filter(id=pk).update(is_disabled=(not medical_category.is_disabled))
    return redirect('ecs.core.views.medical_category.administration')
