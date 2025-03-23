
from flask import Blueprint, request, jsonify
from google.cloud import bigquery
from datetime import datetime
from config.settings import BIGQUERY_TABLES, DEFAULT_SERVICE
from api.services.blob_storage import bucket_folder_creation_for_one_patient, delete_patient_folder
import functions_framework
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
            # Criar pasta no bucket para o novo paciente
            bucket_folder_creation_for_one_patient(patient_id)
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
    
def update_waiting_times(Request):
    try:
        query="""
        SELECT SUBJECT_ID, DATE_DIFF(ADMITTIME, DISCHTIME, HOUR) AS WAITING
        FROM `dream-team-bdcc.Hospital.Admissions` 
        ORDER BY WAITING DESC
        LIMIT 50
        """

        query_job=bigquery_client.query(query)
        results=query_job.result()
        waiting_times=[]
        for row in results:
            waiting_times.append({
                "SUBJECT_ID": str(row.SUBJECT_ID),
                "WAITING": row.WAITING
            })
            
        return "Waiting_List updated."
    except Exception as e:
        return f"Error: {str(e)}"

def delete_patient_from_database(patient_id):
    try:

        update_queries = [
            f"""
            UPDATE `dream-team-bdcc.Hospital.Admissions`
            SET SUBJECT_ID = -1
            WHERE SUBJECT_ID = {patient_id}
            """,
            f"""
            UPDATE `dream-team-bdcc.Hospital.Inputs`
            SET SUBJECT_ID = -1
            WHERE SUBJECT_ID = {patient_id}
            """,
            f"""
            UPDATE `dream-team-bdcc.Hospital.Lab_Events`
            SET SUBJECT_ID = -1
            WHERE SUBJECT_ID = {patient_id}
            """,
            f"""
            UPDATE `dream-team-bdcc.Hospital.Services`
            SET SUBJECT_ID = -1
            WHERE SUBJECT_ID = {patient_id}
            """
        ]
        
        for query in update_queries:
            query_job = bigquery_client.query(query)
            query_job.result()
            
        delete_query = f"""
        DELETE FROM `dream-team-bdcc.Hospital.Patient`
        WHERE SUBJECT_ID = {patient_id}
        """
        
        query_job = bigquery_client.query(delete_query)
        query_job.result()
        
        return True
        
    except Exception as e:
        print(f"Error deleting patient: {str(e)}")
        return False

@patients_bp.route('/rest/patients/<patient_id>', methods=['DELETE'])
def delete_patient_endpoint(patient_id):
    try:

        patient_id = int(patient_id)
        
        db_success = delete_patient_from_database(patient_id)
        if not db_success:
            return jsonify({"error": "Failed to delete patient from database"}), 500
            
        bucket_success = delete_patient_folder(patient_id)
        if not bucket_success:
            return jsonify({"warning": "Patient deleted from database but failed to delete folder from bucket"}), 200
            
        return jsonify({
            "message": "Patient deleted successfully",
            "patient_id": patient_id
        }), 200
            
    except ValueError:
        return jsonify({"error": "Invalid patient ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@patients_bp.route('/rest/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient data"""
    try:
        data = request.get_json()
        
        query = """
        -- Update Patient table
        UPDATE `dream-team-bdcc.Hospital.Patient`
        SET
            GENDER = @genero,
            DOB = PARSE_TIMESTAMP('%Y-%m-%d', @birth_date), 
            DOD = @hora_da_morte, 
            DOD_HOSP = @hora_da_morte_no_hosp,
            DOD_SSN = @hora_da_morte_no_sistema, 
            EXPIRE_FLAG = @se_morreu 
        WHERE SUBJECT_ID = @patient;

        -- Update Services table
        UPDATE `dream-team-bdcc.Hospital.Services`
        SET
            CURR_SERVICE = @doctor
        WHERE SUBJECT_ID = @patient;
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("patient", "INT64", int(patient_id)),
                bigquery.ScalarQueryParameter("genero", "STRING", data.get("gender", None)),
                bigquery.ScalarQueryParameter("birth_date", "STRING", data.get("date_of_birth", None)),
                bigquery.ScalarQueryParameter("hora_da_morte", "TIMESTAMP", data.get("death_time", None)),
                bigquery.ScalarQueryParameter("hora_da_morte_no_hosp", "TIMESTAMP", data.get("hospital_death_time", None)),
                bigquery.ScalarQueryParameter("hora_da_morte_no_sistema", "TIMESTAMP", data.get("ssn_death_time", None)),
                bigquery.ScalarQueryParameter("se_morreu", "INT64", data.get("expired", 0)),
                bigquery.ScalarQueryParameter("doctor", "STRING", data.get("curr_service", None))
            ]
        )
        
        query_job = bigquery_client.query(query, job_config=job_config)
        query_job.result()
        
        return jsonify({
            "message": "Patient updated successfully",
            "patient_id": patient_id
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid patient ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500





#google cloud function to update the waiting list 
@functions_framework.http
def update_waiting_times(Request):
    try:
        query="""
        SELECT SUBJECT_ID, DATE_DIFF(ADMITTIME, DISCHTIME, HOUR) AS WAITING
        FROM `dream-team-bdcc.Hospital.Admissions` 
        ORDER BY WAITING DESC
        LIMIT 50
        """

        query_job=bigquery_client.query(query)
        results=query_job.result()
        waiting_times=[]
        for row in results:
            waiting_times.append({
                "SUBJECT_ID": str(row.SUBJECT_ID),
                "WAITING": row.WAITING
            })
            
        return "Waiting_List updated."
    except Exception as e:
        return f"Error: {str(e)}"
 