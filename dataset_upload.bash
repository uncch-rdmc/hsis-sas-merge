#!/bin/bash

basefld=/sasdata/output

echo "Dataset->"  $1
echo "Result Folder->" $2

export API_TOKEN=
export SERVER_URL=
export PID=$1

cleanpid=${PID//[.:\/]/}
echo $cleanpid
fullpath=$basefld/$cleanpid/$2
echo $fullpath
desc=$2
for filename in $fullpath/*; do
    [ -e "$filename" ] || continue
    echo $filename
    #hardcoded pid for demo. This can lead to name collisions but we are ok with that for the demo
    result=$(curl -H X-Dataverse-key:$API_TOKEN -X POST -F "file=@$filename" -F "jsonData={\"description\":\"Generated via sas code $2\"}" "$SERVER_URL/api/datasets/:persistentId/add?persistentId=doi:10.33563/FK2/HZCZMK")
    echo result

done