from django import forms
from django.conf import settings

class HSISMergeForm(forms.Form):

    #TODO: Do something better instead of overloading this string
    DATASET_CHOICES = [
        #('NC|07|doi:10.33563/FK2/WAXZEH', 'NC 2007'), #Match 1&2 unsupported currently
        ('NC|13|doi:10.33563/FK2/V1JFNA', 'NC 2013'),
        ('NC|15|doi:10.33563/FK2/7RLCDC', 'NC 2015'),
        #('other', 'other') #unsupported currently
    ]

    MERGE_SCRIPT_CHOICES = [
        ('NC_merging_data_for_2017_modifiedByAS_forServer_nolibs.sas', 'NC Merging Data'),
        #('filename 2', 'Merge 1'),
    ]

    # TODO: If we do keep this email field we should make it accept multiple. But we should probably just combine it with the choice field below
    #email = forms.CharField(label='Invitee email', max_length=5, required=False)
    dataset = forms.ChoiceField(choices=DATASET_CHOICES)
    other_dataset = forms.CharField(required=False, label='Other Dataset DOI')
    merge_script = forms.ChoiceField(choices=MERGE_SCRIPT_CHOICES)