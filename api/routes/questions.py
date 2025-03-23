from flask import Blueprint, request, jsonify
from google.cloud import bigquery
from datetime import datetime
from config.settings import BIGQUERY_TABLES

questions_bp = Blueprint('questions', __name__)
bigquery_client = bigquery.Client()

@questions_bp.route('/rest/patients/<patient_id>/question', methods=['POST'])
def create_question(patient_id):
    try:
        data = request.get_json()
        
        if not all(k in data for k in ["curr_service", "message"]):
            return jsonify({
                "error": "Missing required fields. Required: curr_service, message"
            }), 400
            
        query = """
        UPDATE `dream-team-bdcc.Hospital.Services`
        SET PAT_QUESTION = @message,
            PAT_TIMESTAMP = CURRENT_TIMESTAMP()                
        WHERE SUBJECT_ID = @patient
        AND CURR_SERVICE = @service
        AND HADM_ID = (
            SELECT max(HADM_ID) 
            FROM `dream-team-bdcc.Hospital.Services` 
            WHERE SUBJECT_ID = @patient
            AND CURR_SERVICE = @service
        );
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("patient", "INT64", int(patient_id)),
                bigquery.ScalarQueryParameter("service", "STRING", data["curr_service"]),
                bigquery.ScalarQueryParameter("message", "STRING", data["message"])
            ]
        )
        
        query_job = bigquery_client.query(query, job_config=job_config)
        query_job.result()
        
        return jsonify({
            "message": "Question created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questions_bp.route('/rest/patients/<patient_id>/answer', methods=['POST'])
def create_answer(patient_id):
    try:
        data = request.get_json()
        
        if not all(k in data for k in ["curr_service", "answer"]):
            return jsonify({
                "error": "Missing required fields. Required: curr_service, answer"
            }), 400
            
        query = """
        UPDATE `dream-team-bdcc.Hospital.Services`
        SET DOC_ANSWER = @answer,
            DOC_TIMESTAMP = CURRENT_TIMESTAMP()
        WHERE SUBJECT_ID = @patient 
        AND CURR_SERVICE = @service
        AND HADM_ID = (
            SELECT max(HADM_ID) 
            FROM `dream-team-bdcc.Hospital.Services` 
            WHERE SUBJECT_ID = @patient
            AND CURR_SERVICE = @service
        );
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("patient", "INT64", int(patient_id)),
                bigquery.ScalarQueryParameter("service", "STRING", data["curr_service"]),
                bigquery.ScalarQueryParameter("answer", "STRING", data["answer"])
            ]
        )
        
        query_job = bigquery_client.query(query, job_config=job_config)
        query_job.result()
        
        return jsonify({
            "message": "Answer created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questions_bp.route('/rest/patients/<patient_id>/questions', methods=['GET'])
def list_questions(patient_id):
    return get_questions(patient_id)

@questions_bp.route('/rest/questions', methods=['GET'])
def list_all_questions():
    return get_questions()

def get_questions(patient_id=None):
    try:
        query = """
        SELECT 
            SUBJECT_ID as patient_id,
            CURR_SERVICE as service,
            PAT_QUESTION as question,
            PAT_TIMESTAMP as question_time,
            DOC_ANSWER as answer,
            DOC_TIMESTAMP as answer_time
        FROM `dream-team-bdcc.Hospital.Services`
        WHERE 1=1
        """
        
        job_config = bigquery.QueryJobConfig()
        
        if patient_id:
            query += " AND SUBJECT_ID = @patient"
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter("patient", "INT64", int(patient_id))
            ]
            
        query += """
        AND (PAT_QUESTION IS NOT NULL OR DOC_ANSWER IS NOT NULL)
        ORDER BY PAT_TIMESTAMP DESC
        """
        
        query_job = bigquery_client.query(query, job_config=job_config)
        results = query_job.result()
        
        questions = []
        for row in results:
            questions.append({
                "patient_id": str(row.patient_id),
                "service": row.service,
                "question": row.question,
                "question_time": row.question_time.isoformat() if row.question_time else None,
                "answer": row.answer,
                "answer_time": row.answer_time.isoformat() if row.answer_time else None
            })
        
        return jsonify(questions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 