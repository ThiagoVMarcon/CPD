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

def get_lab_test_progress(patient_id):
    query = """
    SELECT 
        ROW_ID,
        SUBJECT_ID,
        HADM_ID,
        ITEMID,
        CHARTTIME,
        VALUE,
        VALUEUOM,
        FLAG,
        LABEL,
        FLUID,
        CATEGORY,
        LOINC_CODE
    FROM `dream-team-bdcc.Hospital.Lab_Test`
    WHERE SUBJECT_ID = @patient_id
    ORDER BY CHARTTIME ASC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("patient_id", "INT64", int(patient_id))
        ]
    )
    
    query_job = bigquery_client.query(query, job_config=job_config)
    results = query_job.result()
    
    lab_tests = []
    for row in results:
        lab_tests.append({
            "row_id": row.ROW_ID,
            "subject_id": str(row.SUBJECT_ID),
            "hadm_id": row.HADM_ID,
            "item_id": row.ITEMID,
            "chart_time": row.CHARTTIME.isoformat() if row.CHARTTIME else None,
            "value": row.VALUE,
            "value_uom": row.VALUEUOM,
            "flag": row.FLAG,
            "label": row.LABEL,
            "fluid": row.FLUID,
            "category": row.CATEGORY,
            "loinc_code": row.LOINC_CODE
        })
    
    return lab_tests

def get_inputs_progress(patient_id):
    query = """
    SELECT
        ROW_ID,
        SUBJECT_ID,
        HADM_ID,
        ICUSTAY_ID,
        STARTTIME,
        ENDTIME,
        ITEMID,
        AMOUNT,
        AMOUNTUOM,
        RATE,
        RATEUOM,
        STORETIME,
        CGID,
        ORDERID,
        LINKORDERID,
        ORDERCATEGORYNAME,
        SECONDARYORDERCATEGORYNAME,
        ORDERCOMPONENTTYPEDESCRIPTION,
        ORDERCATEGORYDESCRIPTION,
        PATIENTWEIGHT,
        TOTALAMOUNT,
        TOTALAMOUNTUOM,
        ISOPENBAG,
        CONTINUEINNEXTDEPT,
        CANCELREASON,
        STATUSDESCRIPTION,
        COMMENTS_EDITEDBY,
        COMMENTS_CANCELEDBY,
        COMMENTS_DATE,
        ORIGINALAMOUNT,
        ORIGINALRATE
    FROM `dream-team-bdcc.Hospital.Inputs`
    WHERE SUBJECT_ID = @patient_id
    ORDER BY STARTTIME ASC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("patient_id", "INT64", int(patient_id))
        ]
    )
    
    query_job = bigquery_client.query(query, job_config=job_config)
    results = query_job.result()
    
    inputs = []
    for row in results:
        inputs.append({
            "row_id": row.ROW_ID,
            "subject_id": str(row.SUBJECT_ID),
            "hadm_id": row.HADM_ID,
            "icustay_id": row.ICUSTAY_ID,
            "start_time": row.STARTTIME.isoformat() if row.STARTTIME else None,
            "end_time": row.ENDTIME.isoformat() if row.ENDTIME else None,
            "item_id": row.ITEMID,
            "amount": row.AMOUNT,
            "amount_uom": row.AMOUNTUOM,
            "rate": row.RATE,
            "rate_uom": row.RATEUOM,
            "store_time": row.STORETIME.isoformat() if row.STORETIME else None,
            "cgid": row.CGID,
            "order_id": row.ORDERID,
            "link_order_id": row.LINKORDERID,
            "order_category_name": row.ORDERCATEGORYNAME,
            "secondary_order_category_name": row.SECONDARYORDERCATEGORYNAME,
            "order_component_type_description": row.ORDERCOMPONENTTYPEDESCRIPTION,
            "order_category_description": row.ORDERCATEGORYDESCRIPTION,
            "patient_weight": row.PATIENTWEIGHT,
            "total_amount": row.TOTALAMOUNT,
            "total_amount_uom": row.TOTALAMOUNTUOM,
            "is_open_bag": row.ISOPENBAG,
            "continue_in_next_dept": row.CONTINUEINNEXTDEPT,
            "cancel_reason": row.CANCELREASON,
            "status_description": row.STATUSDESCRIPTION,
            "comments_edited_by": row.COMMENTS_EDITEDBY,
            "comments_canceled_by": row.COMMENTS_CANCELEDBY,
            "comments_date": row.COMMENTS_DATE.isoformat() if row.COMMENTS_DATE else None,
            "original_amount": row.ORIGINALAMOUNT,
            "original_rate": row.ORIGINALRATE
        })
    
    return inputs 