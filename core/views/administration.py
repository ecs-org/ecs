# -*- coding: utf-8 -*-

from ecs.core.models import AdvancedSettings
from ecs.core.forms import AdvancedSettingsForm
from ecs.utils.viewutils import render
from ecs.users.utils import user_flag_required, user_group_required, sudo


@user_flag_required('is_internal')
@user_group_required('EC-Office')
def advanced_settings(request):
    instance = AdvancedSettings.objects.get(pk=1)
    form = AdvancedSettingsForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return render(request, 'administration/advanced_settings.html', {'form': form})
