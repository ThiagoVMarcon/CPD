from flask import Blueprint, request, jsonify
from google.cloud import bigquery
from datetime import datetime
from config.settings import BIGQUERY_TABLES

admissions_bp = Blueprint('admissions', __name__)
bigquery_client = bigquery.Client()

@admissions_bp.route('/rest/admission', methods=['POST'])
def create_admission():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ["patient_id"]):
            return jsonify({
                "error": "Missing required fields. Required: patient_id"
            }), 400
            
        query = """
        DECLARE ROW_ INT64;
        DECLARE ADM_ID INT64;

        SET ROW_ = (SELECT MAX(ROW_ID) + 1 FROM `dream-team-bdcc.Hospital.Admissions`);
        SET ADM_ID = (SELECT MAX(HADM_ID) + 1 FROM `dream-team-bdcc.Hospital.Admissions`);

        -- Insert into Admissions table
        INSERT INTO `dream-team-bdcc.Hospital.Admissions` 
        (ROW_ID,
        SUBJECT_ID,
        HADM_ID,
        ADMITTIME,
        DISCHTIME,
        DEATHTIME,
        ADMISSION_TYPE,
        ADMISSION_LOCATION,
        DISCHARGE_LOCATION,
        INSURANCE,
        LANGUAGE,
        RELIGION,
        MARITAL_STATUS,
        ETHNICITY,
        EDREGTIME,
        EDOUTTIME,
        DIAGNOSIS,
        HOSPITAL_EXPIRE_FLAG,
        HAS_CHARTEVENTS_DATA
        )
        VALUES
        (ROW_,
        @patient,
        ADM_ID,
        PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%S', @admit_time),
        NULL,
        NULL,
        @admission_type,
        @admission_location,
        NULL,
        @insurance,
        @language,
        NULL,
        NULL,
        NULL,
        CURRENT_TIMESTAMP(),
        NULL,
        @diagnosis,
        0,
        1
        );

        -- Return the generated admission_id
        SELECT ADM_ID as admission_id;
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("patient", "INT64", int(data["patient_id"])),
                bigquery.ScalarQueryParameter("admit_time", "STRING", data.get("admit_time", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))),
                bigquery.ScalarQueryParameter("admission_type", "STRING", data.get("admission_type", "EMERGENCY")),
                bigquery.ScalarQueryParameter("admission_location", "STRING", data.get("admission_location", "EMERGENCY ROOM")),
                bigquery.ScalarQueryParameter("insurance", "STRING", data.get("insurance", "PUBLIC")),
                bigquery.ScalarQueryParameter("language", "STRING", data.get("language", "PORTUGUESE")),
                bigquery.ScalarQueryParameter("diagnosis", "STRING", data.get("diagnosis", "NEW ADMISSION"))
            ]
        )
        
        query_job = bigquery_client.query(query, job_config=job_config)
        results = query_job.result()
        
        for row in results:
            admission_id = str(row.admission_id)
            break
        
        return jsonify({
            "message": "Admission created successfully",
            "admission_id": admission_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admissions_bp.route('/rest/admission/<patient_id>/<admission_id>', methods=['PUT'])
def update_admission(patient_id, admission_id):
    """Update admission data"""
    try:
        data = request.get_json()
        
        query = """
        UPDATE `dream-team-bdcc.Hospital.Admissions`
        SET
            ADMITTIME = @horadeestrada,
            DISCHTIME = @saidahospital, 
            DEATHTIME = @hora_da_morte,
            ADMISSION_TYPE = @stringComOTipo,
            ADMISSION_LOCATION = @local_admissao,
            DISCHARGE_LOCATION = @local_alta, 
            INSURANCE = @seguro, 
            LANGUAGE = @lingua,
            RELIGION = @religiao, 
            MARITAL_STATUS = @marital, 
            ETHNICITY = @cor,
            EDREGTIME = @quehorasveiodeoutr, 
            DIAGNOSIS = @diagnostico, 
            HOSPITAL_EXPIRE_FLAG = @flag_obito, 
            HAS_CHARTEVENTS_DATA = @tem_eventos 
        WHERE SUBJECT_ID = @patient AND HADM_ID = @admission;
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("patient", "INT64", int(patient_id)),
                bigquery.ScalarQueryParameter("admission", "INT64", int(admission_id)),
                bigquery.ScalarQueryParameter("horadeestrada", "TIMESTAMP", data.get("admit_time", None)),
                bigquery.ScalarQueryParameter("saidahospital", "TIMESTAMP", data.get("discharge_time", None)),
                bigquery.ScalarQueryParameter("hora_da_morte", "TIMESTAMP", data.get("death_time", None)),
                bigquery.ScalarQueryParameter("stringComOTipo", "STRING", data.get("admission_type", None)),
                bigquery.ScalarQueryParameter("local_admissao", "STRING", data.get("admission_location", None)),
                bigquery.ScalarQueryParameter("local_alta", "STRING", data.get("discharge_location", None)),
                bigquery.ScalarQueryParameter("seguro", "STRING", data.get("insurance", None)),
                bigquery.ScalarQueryParameter("lingua", "STRING", data.get("language", None)),
                bigquery.ScalarQueryParameter("religiao", "STRING", data.get("religion", None)),
                bigquery.ScalarQueryParameter("marital", "STRING", data.get("marital_status", None)),
                bigquery.ScalarQueryParameter("cor", "STRING", data.get("ethnicity", None)),
                bigquery.ScalarQueryParameter("quehorasveiodeoutr", "TIMESTAMP", data.get("ed_reg_time", None)),
                bigquery.ScalarQueryParameter("diagnostico", "STRING", data.get("diagnosis", None)),
                bigquery.ScalarQueryParameter("flag_obito", "INT64", data.get("expired", 0)),
                bigquery.ScalarQueryParameter("tem_eventos", "INT64", data.get("has_events", 0))
            ]
        )
        
        query_job = bigquery_client.query(query, job_config=job_config)
        result = query_job.result()
        
        return jsonify({
            "message": "Admission updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 