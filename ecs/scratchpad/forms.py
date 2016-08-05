from django import forms

from ecs.scratchpad.models import ScratchPad

class ScratchPadForm(forms.ModelForm):
    class Meta:
        model = ScratchPad
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['class'] = 'form-control'
