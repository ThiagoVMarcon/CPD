from flask import Blueprint, request, jsonify
from google.cloud import bigquery
from datetime import datetime
from config.settings import BIGQUERY_TABLES, DEFAULT_SERVICE

patients_bp = Blueprint('patients', __name__)
bigquery_client = bigquery.Client()

@patients_bp.route('/rest/user', methods=['POST'])
def create_patient():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ["date_of_birth", "gender"]):
            return jsonify({
                "error": "Missing required fields. Required: date_of_birth, gender"
            }), 400
            
        query = """
        DECLARE ROW_ INT64;
        DECLARE SUB_ID INT64;

        SET ROW_ = (SELECT MAX(ROW_ID) + 1 FROM `dream-team-bdcc.Hospital.Patient`);
        SET SUB_ID = (SELECT MAX(SUBJECT_ID) + 1 FROM `dream-team-bdcc.Hospital.Patient`);

        -- Insert into Patient table
        INSERT INTO `dream-team-bdcc.Hospital.Patient` 
        (ROW_ID, SUBJECT_ID, GENDER, DOB, DOD, DOD_HOSP, DOD_SSN, EXPIRE_FLAG)
        VALUES
        (ROW_,
        SUB_ID,
        @gender,
        PARSE_TIMESTAMP('%Y-%m-%d', @date_of_birth),
        NULL,
        NULL,
        NULL,
        0
        );

        -- Insert into Services table
        INSERT INTO `dream-team-bdcc.Hospital.Services` 
        (ROW_ID, SUBJECT_ID, TRANSFERTIME, CURR_SERVICE)
        VALUES
        (
        ROW_,
        SUB_ID,
        CURRENT_TIMESTAMP(),
        @curr_service
        );

        -- Return the generated subject_id
        SELECT SUB_ID as patient_id;
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("date_of_birth", "STRING", data["date_of_birth"]),
                bigquery.ScalarQueryParameter("gender", "STRING", data["gender"]),
                bigquery.ScalarQueryParameter("curr_service", "STRING", data.get("curr_service", DEFAULT_SERVICE))
            ]
        )
        
        query_job = bigquery_client.query(query, job_config=job_config)
        results = query_job.result()
        
        for row in results:
            patient_id = str(row.patient_id)
            break
        
        return jsonify({
            "message": "Patient created successfully",
            "patient_id": patient_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@patients_bp.route('/rest/patient-ids', methods=['GET'])
def get_patient_ids():
    """Get list of all patient IDs"""
    try:
        query = """
        SELECT DISTINCT subject_id
        FROM `dream-team-bdcc.Hospital.Services`
        """
        
        query_job = bigquery_client.query(query)
        results = query_job.result()
        
        patients = [dict(row.items()) for row in results]
        
        return jsonify(patients), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@patients_bp.route('/rest/services', methods=['GET'])
def get_services():
    """Get list of all medical services"""
    try:
        query = """
        SELECT DISTINCT CURR_SERVICE as service
        FROM `dream-team-bdcc.Hospital.Services`
        ORDER BY CURR_SERVICE
        """
        
        query_job = bigquery_client.query(query)
        results = query_job.result()
        
        services = [dict(row.items()) for row in results]
        
        return jsonify(services), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@patients_bp.route('/rest/waiting-list', methods=['GET'])
def get_waiting_list():
    """Get waiting list of patients"""
    try:
        query = """
        SELECT SUBJECT_ID, DATE_DIFF(ADMITTIME, DISCHTIME, HOUR) AS WAITING
        FROM `dream-team-bdcc.Hospital.Admissions` 
        ORDER BY WAITING DESC
        LIMIT 50
        """
        
        query_job = bigquery_client.query(query)
        results = query_job.result()
        
        waiting_list = []
        for row in results:
            waiting_list.append({
                "SUBJECT_ID": str(row.SUBJECT_ID),
                "WAITING": row.WAITING
            })
        
        return jsonify(waiting_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 