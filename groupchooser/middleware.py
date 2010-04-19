from django.contrib.auth.models import Group

class GroupChooserMiddleware(object):
    def process_request(self, request):
        if 'groupchooser-group_pk' in request.session:
            try:
                group = Group.objects.get(pk=request.session['groupchooser-group_pk'])
            except Group.DoesNotExist:
                group = None
            request.usergroup = group