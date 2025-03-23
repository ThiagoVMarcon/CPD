from google.cloud import storage
from google.cloud import bigquery
from config.settings import BUCKET_NAME

storage_client = storage.Client()
bigquery_client = bigquery.Client()

def check_Folder(bucket, patient_id):
    blobs = bucket.list_blobs(prefix=f"patients/{patient_id}/")
    return any(blobs)

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

def add_Image_to_patient_file(patient_id, file_name, file_content):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"patients/{patient_id}/Images/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Image {file_name} uploaded for patient {patient_id}.")
    return True
    
def add_Video_to_patient_file(patient_id, file_name, file_content):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"patients/{patient_id}/Videos/{file_name}")
    blob.upload_from_string(file_content)
    print(f"Video {file_name} uploaded for patient {patient_id}.")
    return True

def list_patient_files(patient_id, file_type="Images"):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=f"patients/{patient_id}/{file_type}/")
    files = [blob.name.split("/")[-1] for blob in blobs if not blob.name.endswith(".keep")]
    return files

def download_patient_file(patient_id, file_name, file_type):
    """
    Download um arquivo específico do bucket para um paciente
    Args:
        patient_id: ID do paciente
        file_name: Nome do arquivo
        file_type: Tipo do arquivo ('Images' ou 'Videos')
    Returns:
        Tupla com (conteúdo do arquivo, tipo do conteúdo)
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # Construir o caminho do arquivo no bucket
        blob_path = f"patients/{patient_id}/{file_type}/{file_name}"
        blob = bucket.blob(blob_path)
        
        # Fazer download do arquivo
        content = blob.download_as_bytes()
        
        # Determinar o content type baseado na extensão
        content_type = 'application/octet-stream'  # default
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            content_type = f'image/{file_name.split(".")[-1].lower()}'
        elif file_name.lower().endswith(('.mp4', '.mov', '.avi')):
            content_type = 'video/mp4' if file_name.lower().endswith('.mp4') else 'video/quicktime'
            
        return content, content_type
        
    except Exception as e:
        print(f"Erro ao fazer download do arquivo: {str(e)}")
        return None, None

def delete_patient_folder(patient_id):
    """
    Deleta a pasta de um paciente e todos seus arquivos do bucket
    Args:
        patient_id: ID do paciente
    Returns:
        bool: True se deletou com sucesso, False caso contrário
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=f"patients/{patient_id}/")
        for blob in blobs:
            blob.delete()
            print(f"Deleted file: {blob.name}")
        print(f"Folder for patient {patient_id} deleted successfully.")
        folder_blob = bucket.blob(f"patients/{patient_id}/")
        if folder_blob.exists():
            folder_blob.delete()
            print(f"Deleted empty folder marker for patient {patient_id}")
        return True
    
    except Exception as e:
        print(f"Error deleting patient folder: {str(e)}")
        return False

# #Create based in query
# def create_folder_forPatients():
#     query_job = bigquery_client.query(
#         """ 
#         SELECT subject_id FROM `dream-team-bdcc.Hospital.Admissions`
#         """
#     )
#     ids_list = query_job.result()
#     patients_ids = [row.subject_id for row in ids_list]
#     if patients_ids:
#         bucket_folder_creation(patients_ids)
#     else:
#         print("No patients found/Error")

# def bucket_folder_creation(patients_ids):
#     bucket = storage_client.get_bucket(BUCKET_NAME)
#     print(f"Bucket '{BUCKET_NAME}' retrieved successfully.")
#     for patient_id in patients_ids:
#         if not check_Folder(bucket, patient_id): 
#             folder_paths = [
#                 f"patients/{patient_id}/Images/.keep",
#                 f"patients/{patient_id}/Videos/.keep"
#             ]
#             print(f"Creating folders for patient_id: {patient_id}")
#             for path in folder_paths:
#                 blob = bucket.blob(path)
#                 blob.upload_from_string("")
#                 print(f"Created folder: {path}")
#         else:
#             print(f"Folder for patient_id: {patient_id} already exists.")


