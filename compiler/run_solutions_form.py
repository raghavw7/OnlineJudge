from django import forms
from .models import Problem, TestCase

Lang_Choice = (
    ('CPP', 'C++'),
    ('Python', 'Python'),
    ('Java', 'Java'),
)


class Add_Problem_Form(forms.ModelForm):
    class Meta:
        model = Problem
        fields = '__all__'

class Edit_Problem_Form(forms.ModelForm):
    class Meta:
        model = Problem
        fields = '__all__'


class Add_Test_Case_Form(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = '__all__'

class Run_Solution_Form(forms.Form):

    language = forms.ChoiceField(required=True, choices=Lang_Choice)
    code = forms.CharField(widget=forms.Textarea)
    input = forms.CharField(widget=forms.Textarea)