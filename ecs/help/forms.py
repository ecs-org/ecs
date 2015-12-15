from django import forms
from ecs.help.models import Page, Attachment

class HelpPageForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ('review_status',)

class AttachmentUploadForm(forms.ModelForm):
    slug = forms.CharField(required=False)

    class Meta:
        model = Attachment
        fields = ('file', 'slug',)

class ImportForm(forms.Form):
    file = forms.FileField()


