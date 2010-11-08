from django import forms
from django.contrib.auth.models import User
from ecs.pdfviewer.models import DocumentAnnotation

class DocumentAnnotationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document')
        super(DocumentAnnotationForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = DocumentAnnotation
        exclude = ('document', 'user', 'author')
        
    def clean_page_number(self):
        page_num = self.cleaned_data['page_number']
        if page_num not in xrange(1, self.document.pages + 1):
            raise forms.ValidationError("page_number must be between 1 and %s" % self.document.pages)
        return page_num
        
class AnnotationSharingForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.all())