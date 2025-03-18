import flask;
from flask import Flask, render_template, jsonify, request;
import google.cloud
from google.cloud import storage
from google.cloud import bigquery
import google.auth
print(google.cloud.storage.__file__)



storage_client=storage.Client()
bigquery_client = bigquery.Client()
Bucket_Name="dreamteambdcc-bucket"

#gotta create the folder for each patient, since we dont have the patience to do for all of them 
#...

def create_folder_forPatients():
    query_job = bigquery_client.query(
        """ 
        SELECT subject_id FROM `dream-team-bdcc.Hospital.Admissions`
        """
    )
    ids_list=query_job.result()
    patients_ids=[row.subject_id for row in ids_list]
    if patients_ids:
        bucket_folder_creation(patients_ids)
    else:
        print("No patients found/Error")



def bucket_folder_creation(patients_ids):
    bucket = storage_client.get_bucket(Bucket_Name)
    print(f"Bucket '{Bucket_Name}' retrieved successfully.")
    for patient_id in patients_ids:
        folder_paths=[
            f"patients/{patient_id}/images/.keep",
            f"patients/{patient_id}/Videos/.keep",
            f"patients/{patient_id}/messages/.keep"
        ]
        print(f"Creating folders for patient_id: {patient_id}")
        for path in folder_paths:
            blob = bucket.blob(path)
            try:
                blob.upload_from_string("")  # This uploads the file as an empty string
                print(f"Created folder: {path}")
            except Exception as e:
                print(f"Failed to create folder {path}: {str(e)}")

    
