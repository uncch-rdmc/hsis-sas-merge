from django import forms
from django.conf import settings

class AuthorInvitationForm(forms.Form):

    DATASET_CHOICES = [
        ('doi1', 'NC 2014'),
        ('doi2', 'NC 2015'),
        ('doi3', 'NC 2016'),
        ('doi4', 'NC 2017'),
        ('other', 'other')
    ]

    MERGE_SCRIPT_CHOICES = [
        ('filename 1', 'Merge 1'),
        ('filename 2', 'Merge 1'),
    ]

    # TODO: If we do keep this email field we should make it accept multiple. But we should probably just combine it with the choice field below
    #email = forms.CharField(label='Invitee email', max_length=5, required=False)
    dataset = forms.ChoiceField(choices=DATASET_CHOICES)
    other_dataset = forms.CharField(required=False, label='Other Dataset DOI')
    merge_script = forms.ChoiceField(choices=MERGE_SCRIPT_CHOICES)