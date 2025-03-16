import concurrent.futures
import flask
from flask import Flask, render_template, jsonify, request
from google.cloud import bigquery

app = Flask(__name__)
bigquery_client = bigquery.Client()

@app.route("/")
def querylimits():
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
        # Set a timeout because queries could take longer than one minute.
        results = query_job.result(timeout=30)
    except concurrent.futures.TimeoutError:
        return render_template("timeout.html", job_id=query_job.job_id)

    # Passando os resultados para o template
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
    app.run(host="127.0.0.1", port=8080, debug=True)
