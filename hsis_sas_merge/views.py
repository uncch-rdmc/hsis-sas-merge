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
# - Before uploading the merge script, I need to edit what years it runs?
#   - Maybe I can just pass an argument into the script... that would be so much better
# - Run merge and return output
#   - This will take time. I don't just want to request to spin. What's the best easy option?
#       - Run an ajax post and when the files are ready a download will begin


# ... Eh the ajax seems overkill. Just use a loading image like this: 
# https://stackoverflow.com/questions/1853662/how-to-show-page-loading-div-until-the-page-has-finished-loading
def index(request):   
    dlpath = ''
    dlpathtext = '' 
    if request.method == 'GET':
        print("GET")
        if(request.GET.get('datasetPid')):
            print(request.GET.get('datasetPid'))
            form = HSISMergeForm(initial={'other_dataset': request.GET.get('datasetPid'),'dataset':'other'})
        else:
            form = HSISMergeForm()
        
    elif request.method == 'POST':
        form = HSISMergeForm(request.POST or None)
        if form.is_valid():
            dataset_selection = form.cleaned_data['dataset']
            if(dataset_selection == "other"):
                #TODO: Right now "other" will blow things up
                dataset_state = form.cleaned_data['other_state']
                dataset_year = form.cleaned_data['other_year']
                dataset_doi = form.cleaned_data['other_dataset']
            else:
                dataset_selection_split_list = dataset_selection.split("|")
                print(dataset_selection_split_list)
                dataset_state = dataset_selection_split_list[0]
                dataset_year = int(dataset_selection_split_list[1])
                dataset_doi = dataset_selection_split_list[2]
        else:
            print(form.errors)

        print(settings.DATAVERSE_URL)
        sas_conn = saspy.SASsession(cfgname='ssh')
        transfer_dataset_files_helper(dataset_doi, sas_conn)
        
        folder_name = get_folder_name_from_doi_helper(dataset_doi)
        sas_conn.endsas() #trying closing and opening the connector because of weird behaviour

        upload_folder_to_sas_helper(folder_name)

        sas_conn = saspy.SASsession(cfgname='ssh')
        print(str(form.cleaned_data))

        #We are just going to store the merge scripts on the sas server for now
        # print(
        #     sas_conn.upload(settings.MEDIA_ROOT+'/merge_scripts/'+form.cleaned_data['merge_script']
        #     , settings.SAS_UPLOAD_FOLDER +"/"+form.cleaned_data['merge_script'], overwrite=False)) #Warning: setting overwrite to true can lead to timeouts?

        if(form.cleaned_data['merge_script'].startswith('NC')):

            #Note: `options dlcreatedir` lets sas create the final folder in a library path if it doesn't exist. Only the final subfolder though, otherwise it fails
            #Note2: the merge scripts live above (..) the input folder
            sas_run_string= "options dlcreatedir; " \
                            "filename scrptfld '"+ settings.SAS_UPLOAD_FOLDER +"/..'; " \
                            "libname e '" + settings.SAS_DOWNLOAD_FOLDER + "/" + folder_name +"'; " \
                            "libname data '" + settings.SAS_UPLOAD_FOLDER + "'; " \
                            "%include scrptfld("+form.cleaned_data['merge_script']+"); "    
                            #"%include scrptfld(NC_merging_data_for_2017_modifiedByAS_forServer_nolibs_dupe.sas); "
            
            #sloppy date handling to deal with 2 digit years
            if(dataset_year <= 7 or dataset_year > 50): #untested
                # 2007 and earlier: Match 1
                print("Match1")
                sas_run_string += "%match1(0"+str(dataset_year)+"); " \
                            "run;"
            elif(dataset_year == 8): #untested
                # 2008: Match 2
                print("Match2")
                sas_run_string += "%match2(0"+str(dataset_year)+"); " \
                            "run;"
            elif(dataset_year == 9):
                # 2009 and later: Match 3 (need added 0 to run string)
                print("Match3")
                sas_run_string += "%match3(0"+str(dataset_year)+"); " \
                            "run;"
            elif(dataset_year > 9 and dataset_year < 30):
                # 2009 and later: Match 3
                print("Match3")
                sas_run_string += "%match3("+str(dataset_year)+"); " \
                            "run;"
        
        elif(form.cleaned_data['merge_script'].startswith('WA')):
            pass

        print(sas_run_string)
        print(str(sas_conn.submit(sas_run_string)).replace('\\n', '\n'))

        #http://irss-dls-buildbox.irss.unc.edu:8888/output/doi1033563FK27RLCDC/
        dlpath = settings.SAS_URL + ":8888/output/"+get_folder_name_from_doi_helper(dataset_doi)
        dlpathtext = "Merge Results"
        sas_conn.endsas()

        #TODO: redirect to a different page so that the form can't resubmit on refresh

    return render(request, 'hsis_sas_merge/form_define_merge.html', {'form': form, 'dlpath': dlpath, 'dlpathtext': dlpathtext})

#Downloads files from dataverse to webserver and then uploads them to saspy
#TODO: Move this to a util folder
def transfer_dataset_files_helper(doi, sas_conn):
    dataset_json = requests.get(settings.DATAVERSE_URL+'/api/datasets/:persistentId/?persistentId='+doi).json()
    #print(dataset_json)

    folder_name = get_folder_name_from_doi_helper(doi)
    directory = settings.MEDIA_ROOT+'/data/'+folder_name
    # If folder exists don't attempt redownload. Good enough for prototype
    # Until Dataverse 5 comes out you can't even get info on original files
    # ... even when it comes out I don't think you can get the md5 on the original file
    if(not os.path.isdir(directory)): 
        for file_json in dataset_json["data"]["latestVersion"]["files"]:
            id = file_json["dataFile"]["id"]
            download_file_from_dataset_helper(folder_name, settings.DATAVERSE_URL+"/api/access/datafile/"+str(id)) #?gbrecs=true&format=original

def download_file_from_dataset_helper(folder_name, url):
    #print(url)
    with requests.get(url+"?format=original", stream=True) as r:
        if(r.status_code == 200):
            print(url+"?format=original")
            d = r.headers['content-disposition']
            fname = re.findall("filename=(.+)", d)[0].strip('\"')
            file_path = settings.MEDIA_ROOT+'/data/'+folder_name+'/'+fname

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        else:
            print(url)
            #Try without "original format" request
            with requests.get(url, stream=True) as r:
                if(r.status_code == 200):
                    #print("success non original format")
                    d = r.headers['content-disposition']
                    fname = re.findall("filename=(.+)", d)[0].strip('\"')
                    file_path = settings.MEDIA_ROOT+'/data/'+folder_name+'/'+fname

                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                else:
                    print("ERROR DOWNLOADING FILES FROM DATASET. ERROR CODE:" + str(r.status_code))
                    pass #TODO: also print error message from server



#Note: This doesn't upload if the files already exist on the sas server
#Also not recursive
#TODO: Upload to a folder with the dataset name, saspy does not support folder creation it seems
#TODO: Check success of upload, involves parsing json
def upload_folder_to_sas_helper(folder_name):
    print("UPLOAD")
    
    for entry in os.scandir(settings.MEDIA_ROOT+'/data/'+folder_name):
        if entry.is_file():
            sas_conn = saspy.SASsession(cfgname='ssh')
            print(entry.path)
            #print(sas_conn.saslog())
            print(sas_conn.upload(entry.path, settings.SAS_UPLOAD_FOLDER +"/"+entry.name, overwrite=True))
            sas_conn.endsas()

## This is broken, at least in OSX. blows up with a socket error
#
# def download_folder_from_sas_helper(folder_name, sas_conn):
#     full_folder_path = settings.SAS_DOWNLOAD_FOLDER+ "/" + folder_name
#     print("DOWNLOAD FOLDER " + full_folder_path)
#     sas_output_list = sas_conn.dirlist(full_folder_path)
#     print(sas_output_list)
#     for entry in sas_output_list:
#         print("downloading from " + full_folder_path + "/" + entry)
#         print("downloading to " + settings.MEDIA_ROOT + "/testtemp/"+ entry)
#         sas_conn.download(settings.MEDIA_ROOT + "/testtemp/"+ entry, full_folder_path + "/" + entry, True)
#         print("downloaded")


    #so... my assumption is that our sas code will output files to a subdirectory using the doi as the folder name

    #First, get list of all files
    # - Are we storing results by year? Or downloading from the same folder by year?
    #Then download each file
    #Finally, present output folder
    
def get_folder_name_from_doi_helper(doi):
    return (''.join(e for e in doi if e.isalnum())) #strips all special characters from doi. Good enough for prototype    

def clear_all_downloads(request):
    if(os.path.isdir(settings.MEDIA_ROOT+"/data")):
        shutil.rmtree(settings.MEDIA_ROOT+"/data")
        return_string = "Deleted Django folder "+settings.MEDIA_ROOT+"/data"
    else:
        return_string = "Django folder "+settings.MEDIA_ROOT+"/data was already deleted, so nothing changed"

    sas_conn = saspy.SASsession(cfgname='ssh')
    # looks like you can just call *nix commands
    sas_run_string = "x 'rm -r "+settings.SAS_UPLOAD_FOLDER+"/*';\n" \
        "run;"
    # sas_run_string= "data _null_;\n " \
    #             "   filename deldir '"+settings.SAS_UPLOAD_FOLDER+"/test';\n " \
    #             "   rc=fdelete('deldir');\n " \
    #             "   put rc=;\n" \
    #             "run;"
    print(sas_run_string)
    print(str(sas_conn.submit(sas_run_string)).replace('\\n', '\n'))
    sas_conn.endsas()
    return_string += "<br><br> Cleared SAS folder " + settings.SAS_UPLOAD_FOLDER

    #TODO: also clear SAS output directory

    return HttpResponse(return_string)