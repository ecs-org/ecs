from django import forms

class RegistrationForm(forms.Form):
    gender = forms.ChoiceField(choices=(('f', 'Frau'), ('m', 'Herr')))
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()


class ActivationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)
    
    def clean_password_again(self):
        password = self.cleaned_data.get("password", "")
        if password != self.cleaned_data["password_again"]:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password

class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField()
