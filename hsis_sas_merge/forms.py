from django import forms
from django.conf import settings

class HSISMergeForm(forms.Form):

    #TODO: Do something better instead of overloading this string
    DATASET_CHOICES = [
        #('NC|07|doi:10.33563/FK2/WAXZEH', 'NC 2007'), #Match 1&2 unsupported currently
        ('NC|11|doi:10.33563/FK2/ERXBTI', 'NC 2011'),
        ('NC|13|doi:10.33563/FK2/V1JFNA', 'NC 2013'),
        ('NC|15|doi:10.33563/FK2/7RLCDC', 'NC 2015'),
        ('WA|11|doi:10.33563/FK2/FLFRU9', 'WA 2011'),
        ('WA|12|doi:10.33563/FK2/A58P7I', 'WA 2012'),
        ('other', 'other') #unsupported currently
    ]

    YEAR_CHOICES = [
        ('--', '----'),
        ('02', '2002'),
        ('03', '2003'),
        ('04', '2004'),
        ('05', '2005'),
        ('06', '2006'),
        ('07', '2007'),
        ('08', '2008'),
        ('09', '2009'),
        ('10', '2010'),
        ('11', '2011'),
        ('12', '2012'),
        ('13', '2013'),
        ('14', '2014'),
        ('15', '2015'),
        ('16', '2016'),
        ('17', '2017'),
        ('18', '2018'),
        ('19', '2019'),
        ('20', '2020')
    ]
    STATE_CHOICES = [
        ('--','--'),
        ('NC','NC'),
        ('WA','WA')
    ]

    MERGE_SCRIPT_CHOICES = [
        ('NC_merging_data_for_2017_django_modular.sas', 'NC Merging Data'),
        ('NC_HSISDataverse_SAS_ordered-logistic-NC-madified-further.sas', 'NC Merging Data with regression'),
        ('WA_ACCURV_modular.sas', 'WA 2-Lane Curve Crashes'),
        #('filename 2', 'Merge 1'),
    ]

    # TODO: If we do keep this email field we should make it accept multiple. But we should probably just combine it with the choice field below
    #email = forms.CharField(label='Invitee email', max_length=5, required=False)
    merge_script = forms.ChoiceField(choices=MERGE_SCRIPT_CHOICES)
    dataset = forms.ChoiceField(choices=DATASET_CHOICES)
    other_dataset = forms.CharField(required=False, label='Dataset DOI')
    other_state = forms.ChoiceField(choices=STATE_CHOICES)
    other_year = forms.ChoiceField(choices=YEAR_CHOICES)