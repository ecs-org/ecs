import tempfile

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Count
from django.utils.text import slugify

from ecs.utils.viewutils import redirect_to_next_url
from ecs.users.utils import user_group_required

from ecs.pki.forms import CertForm
from ecs.pki.models import Certificate


@user_group_required('EC-Signing', 'EC-Office')
def cert_list(request, user_pk=None):
    return render(request, 'pki/cert_list.html', {
        'certs': (
            Certificate.objects
                .select_related('user')
                .annotate(is_revoked=Count('revoked_at'))
                .order_by('is_revoked', 'user__email', 'cn')
        ),
    })


@user_group_required('EC-Signing')
def create_cert(request, user_pk=None):
    form = CertForm(request.POST or None)

    if form.is_valid():
        cn = form.cleaned_data.get('cn').strip()
        user = form.cleaned_data['user']

        with tempfile.NamedTemporaryFile() as tmp:
            cert = Certificate.create_for_user(tmp.name, user, cn=cn,
                passphrase=form.cleaned_data['passphrase'])
            pkcs12 = tmp.read()

        response = HttpResponse(pkcs12, content_type='application/x-pkcs12')
        filename = '{}.p12'.format(slugify(cert.cn))
        response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
        return response
        
    return render(request, 'pki/create_cert.html', {
        'form': form,
    })


@require_POST
@user_group_required('EC-Signing', 'EC-Office')
def revoke_cert(request, cert_pk=None):
    cert = get_object_or_404(Certificate, pk=cert_pk)
    cert.revoke()
    return redirect('ecs.pki.views.cert_list')


def authenticate(request):
    if request.user.profile.is_internal:
        request.session['ecs_pki_authenticated'] = True
        request.session.modified = True
    return redirect_to_next_url(request, reverse('ecs.dashboard.views.view_dashboard'))
    
