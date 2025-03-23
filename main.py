from flask import Flask, render_template, jsonify
# from api.services.blob_storage import create_folder_forPatients
from api.routes.patients import update_waiting_times
from api.routes import (
    patients_bp,
    admissions_bp,
    questions_bp,
    progress_bp,
    media_bp
)
from api.services.queries import (
    get_patient_ids,
    get_services,
    get_waiting_list,
    get_questions,
    get_lab_test_progress,
    get_inputs_progress
)

app = Flask(__name__)

app.register_blueprint(patients_bp)
app.register_blueprint(admissions_bp)
app.register_blueprint(questions_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(media_bp)

@app.route("/")
def home():
    try:
        patients = [{"subject_id": pid} for pid in get_patient_ids()]
        services = [{"service": s} for s in get_services()]
        
        return render_template(
            "bdccIndex.html", 
            patients=patients,  
            services=services,  
            waiting_list=get_waiting_list(),
            questions=get_questions()
        )
    except Exception as e:
        print(f"Error in home route: {str(e)}") 
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

