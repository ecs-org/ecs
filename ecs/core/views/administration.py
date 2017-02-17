from django.shortcuts import render

from ecs.core.models import AdvancedSettings, EthicsCommission
from ecs.core.forms import AdvancedSettingsForm, EthicsCommissionFormSet
from ecs.users.utils import user_group_required


@user_group_required('EC-Office', 'EC-Executive')
def advanced_settings(request):
    instance = AdvancedSettings.objects.get(pk=1)
    form = AdvancedSettingsForm(request.POST or None, request.FILES or None,
        instance=instance, prefix='advanced_settings')
    ec_formset = EthicsCommissionFormSet(request.POST or None,
        queryset=EthicsCommission.objects.order_by('name'),
        prefix='ethics_commissions')
    if request.method == 'POST':
        if form.is_valid():
            form.save()

            f = form.cleaned_data.get('logo_file')
            if f:
                instance.logo = f.read()
                instance.logo_mimetype = f.content_type

            f = form.cleaned_data.get('print_logo_file')
            if f:
                instance.print_logo = f.read()
                instance.print_logo_mimetype = f.content_type

            instance.save()

        if ec_formset.is_valid():
            ec_formset.save()
    return render(request, 'administration/advanced_settings.html', {'form': form, 'ec_formset': ec_formset})
