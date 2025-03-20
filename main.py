import concurrent.futures
import flask
from flask import Flask, render_template, jsonify, request
from google.cloud import bigquery
from BlobFunctions import create_folder_forPatients

app = Flask(__name__)
bigquery_client = bigquery.Client()

@app.route("/")
def home():
    # Buscar lista de pacientes (apenas IDs)
    query_job = bigquery_client.query(
        """
        SELECT DISTINCT subject_id
        FROM `dream-team-bdcc.Hospital.Services`
        """
    )
    
    results = query_job.result()
    patients = [dict(row.items()) for row in results]
    
    # Buscar lista de serviços médicos
    doctors_query = bigquery_client.query(
        """
        SELECT DISTINCT CURR_SERVICE
        FROM `dream-team-bdcc.Hospital.Services`
        ORDER BY CURR_SERVICE
        """
    )
    
    doctors_results = doctors_query.result()
    doctors = [dict(row.items()) for row in doctors_results]
    
    # Buscar lista de espera
    waiting_query = bigquery_client.query(
        """
        SELECT SUBJECT_ID, DATE_DIFF(ADMITTIME, DISCHTIME, HOUR) AS WAITING
        FROM `dream-team-bdcc.Hospital.Admissions` 
        ORDER BY WAITING DESC
        LIMIT 50
        """
    )
    
    waiting_results = waiting_query.result()
    waiting_list = [dict(row.items()) for row in waiting_results]
    
    # Buscar perguntas dos pacientes
    questions_query = bigquery_client.query(
        """
        SELECT 
            SUBJECT_ID AS PATIENT,
            HADM_ID AS ADMISSION,
            PAT_QUESTION AS QUESTION,
            PAT_TIMESTAMP AS TIME_MESSAGE
        FROM `dream-team-bdcc.Hospital.Services`
        WHERE PAT_QUESTION IS NOT NULL
        ORDER BY PAT_TIMESTAMP DESC
        """
    )
    
    questions_results = questions_query.result()
    questions = [dict(row.items()) for row in questions_results]
    
    return render_template("bdccIndex.html", 
                         patients=patients, 
                         doctors=doctors, 
                         questions=questions,
                         waiting_list=waiting_list)

@app.route("/query")
def get_pacient():
    query_job = bigquery_client.query(
        """
        SELECT subject_id
        FROM `dream-team-bdcc.Hospital.Services`
        """
    )
    return flask.redirect(
        flask.url_for(
            "results",
            project_id=query_job.project,
            job_id=query_job.job_id,
            location=query_job.location,
        )
    )

@app.route("/results")
def results():
    project_id = request.args.get("project_id")
    job_id = request.args.get("job_id")
    location = request.args.get("location")

    query_job = bigquery_client.get_job(
        job_id,
        project=project_id,
        location=location,
    )

    try:
        results = query_job.result(timeout=30)
    except concurrent.futures.TimeoutError:
        return render_template("timeout.html", job_id=query_job.job_id)

    return render_template("query_result.html", results=results)

@app.route("/json")
def main():
    query_job = bigquery_client.query(
        """
        SELECT
            subject_id,
            hadm_id,
            admittime
        FROM `dream-team-bdcc.Hospital.Admissions`
        ORDER BY admittime DESC
        LIMIT 10
        """
    )

    results = query_job.result()  # Espera o término da consulta

    data = [
        {"subject_id": row.subject_id, "hadm_id": row.hadm_id, "admittime": row.admittime}
        for row in results
    ]

    return jsonify(data)  # Retorna os resultados como JSON

if __name__ == "__main__":
    # create_folder_forPatients()
    app.run(host="127.0.0.1", port=8080, debug=True)

