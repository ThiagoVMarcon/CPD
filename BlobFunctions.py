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





#creates a folder like structure for the patient---Organizes in "folder Images, Videos or Messages"

def bucket_folder_creation(patients_ids):
    bucket = storage_client.get_bucket(Bucket_Name)
    print(f"Bucket '{Bucket_Name}' retrieved successfully.")
    for patient_id in patients_ids:
        if not check_Folder(bucket, patient_id): 
            folder_paths=[
            f"patients/{patient_id}/Images/.keep",
            f"patients/{patient_id}/Videos/.keep",
            f"patients/{patient_id}/Messages/.keep"
            ]
            print(f"Creating folders for patient_id: {patient_id}")
            for path in folder_paths:
                blob = bucket.blob(path)
                blob.upload_from_string("")
                print(f"Created folder: {path}")
        else:
            print(f"Folder for patient_id: {patient_id} already exists.")




#just to check the folder like this we dont need to recreate everything unless we delete in the cloud
def check_Folder(bucket, patient_id):
    blobs = bucket.list_blobs(prefix=f"patients/{patient_id}/")
    return any(blobs)

#UPLOAD FUNCTIONS-------------------------------------
    



def add_Images_to_patient_file(patient_id,file_name,file_content):
    bucket=storage_client.get_bucket(Bucket_Name)
    blob=bucket.blob(f"patients/{patient_id}/Images/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Image{file_name} uploaded for patient{patient_id}.")
    
def add_Videos_to_patient_file(patient_id,file_name,file_content):
    bucket=storage_client.get_bucket(Bucket_Name)
    blob=bucket.blob(f"patients/{patient_id}/Videos/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Video{file_name} uploaded for patient{patient_id}.")

def add_Messages_to_patient_file(patient_id,file_name,file_content):
    bucket=storage_client.get_bucket(Bucket_Name)
    blob=bucket.blob(f"patients/{patient_id}/Messages/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Message{file_name} uploaded for patient{patient_id}.")


#RETRIEVE FUNCTIONS---------------------------------------------------------
#to retrieve the images and videos 
def list_patient_files(patient_id, file_type="Images"):
    bucket=storage_client.get_bucket(Bucket_Name)
    blobs=bucket.list_blobs(prefix=f"patients/{patient_id}/{file_type}/")
    files=[blob.name.split("/")[-1] for blob in blobs if not blob.name.endswith(".keep")]
    return files

#to retrieve messages
def list_patient_messages(patient_id):
    bucket=storage_client.get_bucket(Bucket_Name)
    blobs=bucket.list_blobs(prefix=f"patients/{patient_id}/Messages/")
    message_files=[blob.name.split("/")[2] for blob in blobs if not blob.name.endswith(".keep")]
    return message_files

#to delete the folder based on patient ID-------------
def delete_patient_folder(patient_id):
    bucket=storage_client.get_bucket(Bucket_Name)
    folder_prefix= f"patients/{patient_id}/"
    blobs=bucket.list_blobs(folder_prefix)
    if not blobs:
        print(f"No files found for patient{patient_id}.")
        return
    for blob in blobs:
        blob.delete()
        print(f"Deleted file: {blob.name}")
    print(f"Folder for patient{patient_id} deleted successfully.")