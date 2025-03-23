from flask import Blueprint, request, jsonify
from google.cloud import storage
from api.services.blob_storage import (
    create_folder_forPatients,
    add_image_toPatientFile,
    add_video_toPatientFile,
    add_message_toPatientFile,
    list_patient_files,
    list_patient_messages
)

media_bp = Blueprint('media', __name__)

@media_bp.route('/rest/patients/<patient_id>/files', methods=['GET'])
def get_patient_files(patient_id):
    try:
        files = list_patient_files(patient_id)
        return jsonify(files), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/patients/<patient_id>/messages', methods=['GET'])
def get_patient_messages(patient_id):
    try:
        messages = list_patient_messages(patient_id)
        return jsonify(messages), 200
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
            
        if not file.content_type.startswith('image/'):
            return jsonify({"error": "File must be an image"}), 400
            
        success = add_image_toPatientFile(patient_id, file)
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
            
        if not file.content_type.startswith('video/'):
            return jsonify({"error": "File must be a video"}), 400
            
        success = add_video_toPatientFile(patient_id, file)
        if success:
            return jsonify({"message": "Video uploaded successfully"}), 201
        else:
            return jsonify({"error": "Failed to upload video"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/patients/<patient_id>/message', methods=['POST'])
def upload_patient_message(patient_id):
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        success = add_message_toPatientFile(patient_id, file)
        if success:
            return jsonify({"message": "Message uploaded successfully"}), 201
        else:
            return jsonify({"error": "Failed to upload message"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/rest/setup-folders', methods=['POST'])
def setup_patient_folders():
    try:
        success = create_folder_forPatients()
        if success:
            return jsonify({"message": "Patient folders created successfully"}), 201
        else:
            return jsonify({"error": "Failed to create patient folders"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500 