from django.shortcuts import render, redirect
from hsis_sas_merge.forms import *

#Do:
# Page to select data and script to run:
# - Create a dropdown and textbox to select the dataset to pull files from
# - Create a dropdown to select the script to run (stored on server)
# - Go button
# - Needs styling
# When posted:
# - Download files from dv (if already stored locally use existing copies?)
# - Run merge and return output
#   - This will take time. I don't just want to request to spin. What's the best easy option?
#       - Run an ajax post and when the files are ready a download will begin

def index(request):
    form = AuthorInvitationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            dataset = form.cleaned_data['dataset']
            if(dataset == "other"):
                dataset =form.cleaned_data['other_dataset']
        else:
            print(form.errors)
    return render(request, 'hsis-sas-merge/form_define_merge.html', {'form': form})
