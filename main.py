from flask import Flask, render_template, jsonify
from api.routes import (
    patients_bp,
    admissions_bp,
    questions_bp,
    # media_bp  # Não usado no momento
)
from api.services.queries import (
    get_patient_ids,
    get_services,
    get_waiting_list,
    get_questions
)

app = Flask(__name__)

# Registrar os blueprints
app.register_blueprint(patients_bp)
app.register_blueprint(admissions_bp)
app.register_blueprint(questions_bp)
# app.register_blueprint(media_bp)  # Não usado no momento

@app.route("/")
def home():
    try:
        # Obter dados
        patients = [{"subject_id": pid} for pid in get_patient_ids()]
        services = [{"service": s} for s in get_services()]
        
        return render_template(
            "bdccIndex.html", 
            patients=patients,  # Mudado de patient_ids para patients
            services=services,  # Adicionado o formato correto
            waiting_list=get_waiting_list(),
            questions=get_questions()
        )
    except Exception as e:
        print(f"Error in home route: {str(e)}") 
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

