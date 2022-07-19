from django import forms
from .models import Team


class TeamCreationForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ['name', 'description']


	def check_name_availability(self, name):
		print("CHECKK")
		name = name.lower()

		teams = Team.objects.all()

		for team in teams:
			team_name = team.name.lower()
			if team_name == name:
				raise forms.ValidationError(f'{name} is already in use')
			#team = Team.objects.exclude(id=self.instance.id).get(name=name).lower().exclude(id=self.instance.id).get(name=name)

		return name
