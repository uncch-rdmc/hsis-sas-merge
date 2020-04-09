from django.shortcuts import render, redirect
from hsis_sas_merge.forms import *
from django.conf import settings
from django.http import HttpResponse
import requests
import shutil
import re
import os
import saspy

#Do:
# Page to select data and script to run:
# - Create a dropdown and textbox to select the dataset to pull files from
# - Create a dropdown to select the script to run (stored on server)
# - Go button
# - Needs styling
# When posted:
# - Download files from dv (if already stored locally use existing copies?)
#   - These files don't actually need to be in the djanog app at all... We could instead download them on the remote server?
#   - Could also just scp them to the server...
#       - saspy has an upload command
#           - We can use upload without override and clear all files if needed
# - Run merge and return output
#   - This will take time. I don't just want to request to spin. What's the best easy option?
#       - Run an ajax post and when the files are ready a download will begin


# ... Eh the ajax seems overkill. Just use a loading image like this: 
# https://stackoverflow.com/questions/1853662/how-to-show-page-loading-div-until-the-page-has-finished-loading
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
        sas_conn = saspy.SASsession(cfgname='ssh')
        transfer_dataset_files_helper(dataset_doi, sas_conn) #TODO: error sometimes on server reload as its unset in a post
        #Now upload the script
        print(
            sas_conn.upload(settings.MEDIA_ROOT+'/merge_scripts/'+form.cleaned_data['merge_script']
            , settings.SAS_UPLOAD_FOLDER +"/"+form.cleaned_data['merge_script'], overwrite=False)) #Warning: setting overwrite to true can lead to timeouts?

    return render(request, 'hsis_sas_merge/form_define_merge.html', {'form': form})

#Downloads files from dataverse to webserver and then uploads them to saspy
#TODO: Move this to a util folder
def transfer_dataset_files_helper(doi, sas_conn):
    dataset_json = requests.get(settings.DATAVERSE_URL+'/api/datasets/:persistentId/?persistentId='+doi).json()
    print(dataset_json)

    folder_name_doi = ''.join(e for e in doi if e.isalnum()) #strips all special characters from doi. Good enough for prototype
    directory = settings.MEDIA_ROOT+'/'+folder_name_doi
    # If folder exists don't attempt redownload. Good enough for prototype
    # Until Dataverse 5 comes out you can't even get info on original files
    # ... even when it comes out I don't think you can get the md5 on the original file
    if(not os.path.isdir(directory)): 
        for file_json in dataset_json["data"]["latestVersion"]["files"]:
            id = file_json["dataFile"]["id"]
            download_file_local_helper(folder_name_doi, settings.DATAVERSE_URL+"/api/access/datafile/"+str(id)+"?format=original&gbrecs=true")
    
    upload_folder_to_sas_helper(folder_name_doi, sas_conn)

    #scp -i ~/.ssh/saspycampus -P 10808 -r /Users/madunlap/Documents/hsis_django_downloads/doi1033563FK2ABQF9V odum@irss-dls-buildbox.irss.unc.edu


def download_file_local_helper(folder_name, url):
    with requests.get(url, stream=True) as r:
        d = r.headers['content-disposition']
        fname = re.findall("filename=(.+)", d)[0].strip('\"')
        file_path = settings.MEDIA_ROOT+'/'+folder_name+'/'+fname

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

#Note: This doesn't upload if the files already exist on the sas server
#Also not recursive
#TODO: Upload to a folder with the dataset name, saspy does not support folder creation it seems
#TODO: Check success of upload, involves parsing json
def upload_folder_to_sas_helper(folder_name, sas_conn):
    print("HEY")
    for entry in os.scandir(settings.MEDIA_ROOT+'/'+folder_name):
        if entry.is_file():
            print(entry.path)
            #print(sas_conn.saslog())
            print(sas_conn.upload(entry.path, settings.SAS_UPLOAD_FOLDER +"/"+entry.name, overwrite=False))

def clear_all_downloads(request):
    shutil.rmtree(settings.MEDIA_ROOT+'/')
    #TODO: Also clear files from SAS server? Wait this is impossible using saspy...

    return HttpResponse("Cleared "+settings.MEDIA_ROOT+'/')