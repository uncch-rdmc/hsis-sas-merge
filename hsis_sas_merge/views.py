from django.shortcuts import render, redirect
from hsis_sas_merge.forms import *
from django.conf import settings
from django.http import HttpResponse
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
            dataset_doi = form.cleaned_data['dataset']
            if(dataset_doi == "other"):
                dataset_doi = form.cleaned_data['other_dataset']
        else:
            print(form.errors)
        print(settings.DATAVERSE_URL)
        download_dataset_files_helper(dataset_doi)
    
    return render(request, 'hsis-sas-merge/form_define_merge.html', {'form': form})

#TODO: Move this to a util folder
def download_dataset_files_helper(doi):
    dataset_json = requests.get(settings.DATAVERSE_URL+'/api/datasets/:persistentId/?persistentId='+doi).json()
    print(dataset_json)

    folder_name_doi = ''.join(e for e in doi if e.isalnum()) #strips all special characters from doi. Good enough for prototype

    # If folder exists don't attempt redownload. Good enough for prototype
    # Until Dataverse 5 comes out you can't even get info on original files
    # ... even when it comes out I don't think you can get the md5 on the original file
    if(not os.path.isdir(settings.MEDIA_ROOT+'/'+folder_name_doi)): 
        for file_json in dataset_json["data"]["latestVersion"]["files"]:
            id = file_json["dataFile"]["id"]
            download_file_helper(folder_name_doi, settings.DATAVERSE_URL+"/api/access/datafile/"+str(id)+"?format=original&gbrecs=true")

def download_file_helper(folder_name, url):
    with requests.get(url, stream=True) as r:
        d = r.headers['content-disposition']
        fname = re.findall("filename=(.+)", d)[0].strip('\"')
        file_path = settings.MEDIA_ROOT+'/'+folder_name+'/'+fname

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def clear_all_downloads(request):
    shutil.rmtree(settings.MEDIA_ROOT+'/')
    return HttpResponse("Cleared "+settings.MEDIA_ROOT+'/')