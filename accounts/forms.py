from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import User, UserAICreds


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        labels = {'email': 'Email'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email


class UserLoginForm(forms.Form):
    username = forms.CharField(
        label='Username', max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        required=True,
        max_length=150
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        labels = {'email': 'Email'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email


class PasswordUpdateForm(forms.Form):
    password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}),
        required=True,
        max_length=150
    )
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        required=True,
        max_length=150
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        required=True,
        max_length=150
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("New password and Confirm password fields must match.")

        # Validate the new password against Django’s password validators
        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error('password1', e)

        return cleaned_data


class AIDocsUploaderForm(forms.Form):
    docs_file = forms.FileField(required=True)


class UserAICredsForm(forms.ModelForm):
    class Meta:
        model = UserAICreds
        fields = ['name_keys_object', 'pinecone_api_key', 'pinecone_index_name', 'groq_api_key']
