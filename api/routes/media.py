from flask import Blueprint, request, jsonify, send_file
from google.cloud import storage
from io import BytesIO
import zipfile
from api.services.blob_storage import (
    bucket_folder_creation_for_one_patient,
    add_Image_to_patient_file,
    add_Video_to_patient_file,
    list_patient_files,
    download_patient_file
)

media_bp = Blueprint('media', __name__)

@media_bp.route('/rest/patients/<patient_id>/files', methods=['GET'])
def get_patient_files(patient_id):
    try:
        images = list_patient_files(patient_id, 'Images')
        videos = list_patient_files(patient_id, 'Videos')
        
        all_files = {
            'images': images,
            'videos': videos
        }
        
        return jsonify(all_files), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/patients/<patient_id>/image', methods=['POST'])
def upload_patient_image(patient_id):
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        success = add_Image_to_patient_file(patient_id, file.filename, file.read())
        if success:
            return jsonify({"message": "Image uploaded successfully"}), 201
        else:
            return jsonify({"error": "Failed to upload image"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/patients/<patient_id>/video', methods=['POST'])
def upload_patient_video(patient_id):
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        success = add_Video_to_patient_file(patient_id, file.filename, file.read())
        if success:
            return jsonify({"message": "Video uploaded successfully"}), 201
        else:
            return jsonify({"error": "Failed to upload video"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/patients/<patient_id>/download/<file_type>/<file_name>', methods=['GET'])
def download_file(patient_id, file_type, file_name):
    try:
        # Verificar se o tipo de arquivo é válido
        if file_type not in ['Images', 'Videos']:
            return jsonify({"error": "Invalid file type. Must be 'Images' or 'Videos'"}), 400
            
        # Fazer download do arquivo
        content, content_type = download_patient_file(patient_id, file_name, file_type)
        
        if content is None:
            return jsonify({"error": "File not found or error downloading"}), 404
            
        # Criar um objeto BytesIO para enviar o arquivo
        file_obj = BytesIO(content)
        
        # Enviar o arquivo como resposta
        return send_file(
            file_obj,
            mimetype=content_type,
            as_attachment=True,
            download_name=file_name
        )
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/patients/<patient_id>/download/all', methods=['GET'])
def download_all_files(patient_id):
    try:
        # Criar um buffer para o arquivo ZIP
        zip_buffer = BytesIO()
        
        # Criar o arquivo ZIP
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Buscar lista de arquivos
            files = {
                'Images': list_patient_files(patient_id, 'Images'),
                'Videos': list_patient_files(patient_id, 'Videos')
            }
            
            # Adicionar cada arquivo ao ZIP
            for file_type, file_list in files.items():
                for file_name in file_list:
                    content, _ = download_patient_file(patient_id, file_name, file_type)
                    if content:
                        # Salvar no ZIP mantendo a estrutura de pastas
                        zip_file.writestr(f"{file_type}/{file_name}", content)
        
        # Preparar o buffer para leitura
        zip_buffer.seek(0)
        
        # Enviar o arquivo ZIP
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'patient_{patient_id}_files.zip'
        )
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @media_bp.route('/rest/setup-folders', methods=['POST'])
# def setup_patient_folders():
#     try:
#         success = create_folder_forPatients()
#         if success:
#             return jsonify({"message": "Patient folders created successfully"}), 201
#         else:
#             return jsonify({"error": "Failed to create patient folders"}), 500
            
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500 