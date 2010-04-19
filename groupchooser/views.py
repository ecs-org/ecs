from django.http import HttpResponseRedirect
from ecs.groupchooser.forms import GroupChooserForm

def choose(request):
    form = GroupChooserForm(request.POST)
    if form.is_valid():
        request.session['groupchooser-group_pk'] = getattr(form.cleaned_data.get('group'), 'pk', None)
    return HttpResponseRedirect(request.GET.get('url', '/'))