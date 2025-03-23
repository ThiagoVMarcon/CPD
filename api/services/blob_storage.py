from google.cloud import storage
from google.cloud import bigquery
from config.settings import BUCKET_NAME

storage_client = storage.Client()
bigquery_client = bigquery.Client()


#Create based in query
def create_folder_forPatients():
    query_job = bigquery_client.query(
        """ 
        SELECT subject_id FROM `dream-team-bdcc.Hospital.Admissions`
        """
    )
    ids_list = query_job.result()
    patients_ids = [row.subject_id for row in ids_list]
    if patients_ids:
        bucket_folder_creation(patients_ids)
    else:
        print("No patients found/Error")

def bucket_folder_creation(patients_ids):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' retrieved successfully.")
    for patient_id in patients_ids:
        if not check_Folder(bucket, patient_id): 
            folder_paths = [
                f"patients/{patient_id}/Images/.keep",
                f"patients/{patient_id}/Videos/.keep"
            ]
            print(f"Creating folders for patient_id: {patient_id}")
            for path in folder_paths:
                blob = bucket.blob(path)
                blob.upload_from_string("")
                print(f"Created folder: {path}")
        else:
            print(f"Folder for patient_id: {patient_id} already exists.")

def check_Folder(bucket, patient_id):
    blobs = bucket.list_blobs(prefix=f"patients/{patient_id}/")
    return any(blobs)


#Create just one patient

def bucket_folder_creation_for_one_patient(patient_id):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' retrieved successfully.")
    if not check_Folder(bucket, patient_id): 
        folder_paths = [
            f"patients/{patient_id}/Images/.keep",
            f"patients/{patient_id}/Videos/.keep"
        ]
        print(f"Creating folders for patient_id: {patient_id}")
        for path in folder_paths:
            blob = bucket.blob(path)
            blob.upload_from_string("")
            print(f"Created folder: {path}")
    else:
        print(f"Folder for patient_id: {patient_id} already exists.")

#Post
def add_Images_to_patient_file(patient_id, file_name, file_content):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"patients/{patient_id}/Images/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Image {file_name} uploaded for patient {patient_id}.")
    
def add_Videos_to_patient_file(patient_id, file_name, file_content):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"patients/{patient_id}/Videos/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Video {file_name} uploaded for patient {patient_id}.")


#Get 
def list_patient_files(patient_id, file_type="Images"):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=f"patients/{patient_id}/{file_type}/")
    files = [blob.name.split("/")[-1] for blob in blobs if not blob.name.endswith(".keep")]
    return files




