from google.cloud import bigquery

bigquery_client = bigquery.Client()

def get_patient_ids():
    query = """
    SELECT DISTINCT SUBJECT_ID 
    FROM `dream-team-bdcc.Hospital.Services`
    """
    job = bigquery_client.query(query)
    return [str(row.SUBJECT_ID) for row in job.result()]

def get_services():
    query = """
    SELECT DISTINCT CURR_SERVICE 
    FROM `dream-team-bdcc.Hospital.Services`
    WHERE CURR_SERVICE IS NOT NULL
    ORDER BY CURR_SERVICE
    """
    job = bigquery_client.query(query)
    return [row.CURR_SERVICE for row in job.result()]

def get_waiting_list():
    """Retorna lista de espera atual"""
    query = """
    SELECT SUBJECT_ID, DATE_DIFF(ADMITTIME, DISCHTIME, HOUR) AS WAITING
    FROM `dream-team-bdcc.Hospital.Admissions` 
    ORDER BY WAITING DESC
    LIMIT 50
    """
    job = bigquery_client.query(query)
    return [{"SUBJECT_ID": str(row.SUBJECT_ID), "WAITING": row.WAITING} for row in job.result()]

def get_questions():
    query = """
    SELECT 
        SUBJECT_ID,
        CURR_SERVICE,
        PAT_QUESTION,
        PAT_TIMESTAMP,
        DOC_ANSWER,
        DOC_TIMESTAMP
    FROM `dream-team-bdcc.Hospital.Services`
    WHERE PAT_QUESTION IS NOT NULL OR DOC_ANSWER IS NOT NULL
    ORDER BY PAT_TIMESTAMP DESC
    """
    job = bigquery_client.query(query)
    questions = []
    for row in job.result():
        questions.append({
            "patient_id": str(row.SUBJECT_ID),
            "service": row.CURR_SERVICE,
            "question": row.PAT_QUESTION,
            "question_time": row.PAT_TIMESTAMP.isoformat() if row.PAT_TIMESTAMP else None,
            "answer": row.DOC_ANSWER,
            "answer_time": row.DOC_TIMESTAMP.isoformat() if row.DOC_TIMESTAMP else None
        })
    return questions 