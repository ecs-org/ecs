from django.conf.urls import url

from ecs.billing import views


urlpatterns = (
    url(r'^submissions/$', views.submission_billing),
    url(r'^invoice/(?P<invoice_pk>\d+)/$', views.view_invoice),
    url(r'^invoices/$', views.invoice_list),

    url(r'^external_review/$', views.external_review_payment),
    url(r'^payment/(?P<payment_pk>\d+)/$', views.view_checklist_payment),
    url(r'^payments/$', views.checklist_payment_list),
    url(r'^external_review/reset/$', views.reset_external_review_payment),
)
