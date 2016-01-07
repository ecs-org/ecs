from django.shortcuts import render

from ecs.core.models import AdvancedSettings, EthicsCommission
from ecs.core.forms import AdvancedSettingsForm, EthicsCommissionFormSet
from ecs.users.utils import user_flag_required, user_group_required


@user_flag_required('is_internal')
@user_group_required('EC-Office', 'EC-Executive Board Group')
def advanced_settings(request):
    instance = AdvancedSettings.objects.get(pk=1)
    form = AdvancedSettingsForm(request.POST or None, instance=instance, prefix='advanced_settings')
    ec_formset = EthicsCommissionFormSet(request.POST or None, queryset=EthicsCommission.objects.all(), prefix='ethics_commissions')
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        if ec_formset.is_valid():
            ec_formset.save()
    return render(request, 'administration/advanced_settings.html', {'form': form, 'ec_formset': ec_formset})
