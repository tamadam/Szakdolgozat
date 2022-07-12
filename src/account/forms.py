from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Character


#customize usercreation form
class AccountRegistrationForm(UserCreationForm):
	character_type = forms.ChoiceField(choices=Character.ROLES)

	class Meta:
		model = Account
		fields = ['username', 'email', 'password1', 'password2']



class AccountEditForm(forms.ModelForm):

	class Meta:
		model = Account
		fields = ['username', 'email', 'profile_image']


	def check_username_availability(self):
		username = self.cleaned_data['username'].lower()
		try:
			account = Account.objects.exclude(id=self.instance.id).get(username=username)
		except Account.DoesNotExist:
			return username
		raise forms.ValidationError(f'{username} is already in use')
		

	def check_email_availability(self):
		email = self.cleaned_data['email'].lower() # ##email az a htmlben az input neve##
		try:
			account = Account.objects.exclude(id=self.instance.id).get(email=email)
		except Account.DoesNotExist:
			return email
		raise forms.ValidationError(f'{email} is already in use')


