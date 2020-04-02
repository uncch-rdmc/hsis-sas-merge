from django.shortcuts import render, redirect
from hsis_sas_merge.forms import *
from django.conf import settings
import requests
import shutil
import re
import os

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
                dataset = form.cleaned_data['other_dataset']
        else:
            print(form.errors)

        print(settings.DATAVERSE_URL)
        #Here download files from dataverse

    download_dataset_files_helper("fake")

    return render(request, 'hsis-sas-merge/form_define_merge.html', {'form': form})

#TODO: Move this to a util folder
def download_dataset_files_helper(doi):
    print("GO!")
    doi_folder = ''.join(e for e in doi if e.isalnum()) #strips all special characters from doi. Good enough for prototype
    download_file_helper(doi_folder, "https://highwaysafetytest.irss.unc.edu/api/access/datafile/16?format=original&gbrecs=true")
    

    #So here I need to download the files.
    #First I need to use the DOI to get all the files in the dataset
    #Then My options then are to either download each one manually
    # - https://dataverse5.odum.unc.edu/api/access/datafile/71?format=original&gbrecs=true
    #Or do a bulk download and unzip
    # - https://dataverse5.odum.unc.edu/api/access/datafiles/71,72?gbrecs=true&format=original
    #
    #Probably will do the first one
    pass


def download_file_helper(folder_name, url):
    with requests.get(url, stream=True) as r:
        d = r.headers['content-disposition']
        fname = re.findall("filename=(.+)", d)[0].strip('\"')
        file_path = settings.MEDIA_ROOT+'/'+folder_name+'/'+fname
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return fname