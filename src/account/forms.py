from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Character


#customize usercreation form
class AccountRegistrationForm(UserCreationForm):
	character_type = forms.ChoiceField(choices=Character.ROLES)

	class Meta:
		model = Account
		fields = ['username', 'email', 'password1', 'password2']

