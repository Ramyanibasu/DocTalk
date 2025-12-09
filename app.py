from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "replace_this_with_a_secure_random_key"  


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "krishna",
    "database": "Doctalk"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

DISEASES = {
    "brain stroke": {
        "title": "Brain Stroke",
        "symptoms": "Facial deviation, Weakness of one side of Body, Slurred speech, Vision loss, Imbalance.",
        "investigations": "CT scan, Brain MRI, Angiogram, Echocardiogram, Blood Test.",
        "treatments": "Aspirin, Atorvastatin, Lipid control.",
        "additional": "No Smoke, No Alcohol, Low fat diet, Disciplined lifestyle."
    },
    "epilepsy": {
        "title": "Epilepsy",
        "symptoms": "Loss of consciousness, Up-rolling eye, Gaze deviation, Tongue bite, Frothing from mouth, Incontinence.",
        "investigations": "EEG, Blood test, Brain MRI.",
        "treatments": "Anti epileptic drugs.",
        "additional": "Adequate sleep, Less Screen Time, Avoid stress."
    },
    "parkinson's": {
        "title": "Parkinsons's",
        "symptoms": "Tremor, Slowness, Imbalance, Stiffness.",
        "investigations": "Brain MRI, TRODAT scan, Blood test.",
        "treatments": "Levodopa, Dopamin agonist.",
        "additional": "Physiotherapy."
    },
    "multiple sclerosis": {
        "title": "Multiple Sclerosis",
        "symptoms": "Sudden imbalance, Sudden vision dysfunction, Weakness of limbs, Abnormal sensations, Feeling of tightness in limbs.",
        "investigations": "Brain & Spine MRI (plain & contrast), CSF study, Blood test, Nerve function test.",
        "treatments": "IVIG, IV steroid, Disease modulator.",
        "additional": "Avoid infection, Avoid heat, Stressfree life."
    },
    "motor neuron disease": {
        "title": "Motor Neuron Disease",
        "symptoms": "Gradual weakness of limbs/trunk, Fasciculation, Difficulty in swallowing, Slurred speech, Muscle wasting.",
        "investigations": "Nerve function test, EMG, Muscle biopsy.",
        "treatments": "Rilutor, Supportive(not curable)",
        "additional": "Good diet, Muscle building exercises"
    },
    "huntington's disease": {
        "title": "Huntington's Disease",
        "symptoms": "Chorea(dancing movements), Abnormal posturing, Dementia, psychiatric issues.",
        "investigations": "Brain MRI, Genetic testing.",
        "treatments": "Symptomatic - tetrabenazine.",
        "additional": "Genetic counselling."
    },
    "gb syndrome": {
        "title": "GB Syndrome",
        "symptoms": "Acute onset ascending weakness of limbs, Difficulty in breathing, Difficulty in swallowing.",
        "investigations": "Nerve function test, CSF, Blood test.",
        "treatments": "IVIG, Steroid, Supportive(including ventilation)",
        "additional": "Physiotherapy"
    },
    "dementia": {
        "title": "Dementia",
        "symptoms": "Impaired short term memory, Confabulation, Inability to learn, Behavioral abnormalities",
        "investigations": "Brain MRI, MOCA (montreal cognitive assessment), FDG PET",
        "treatments": "Pharmacotherapy, Cognitive therapy",
        "additional": "Playing chess, Scrabble, Crossword puzzles"
    },
    "neuropathy": {
        "title": "Neuropathy",
        "symptoms": "Pain in limbs, Numbness & tingling in limbs, muscle wasting, weakness in limbs",
        "investigations": "Nerve function test, Blood test",
        "treatments": "Symptomatic, Steroid, Disease modulator",
        "additional": "Physiotherapy, Magnetic stimulation"
    },
    "myasthenia gravis": {
        "title": "Myasthenia Gravis",
        "symptoms": "Ptosis(drooping eyes), Muscle weakness, Exercise induced weakness, Diurnal variation",
        "investigations": "RNST, ACHR, Antibody test, Neostigmine test",
        "treatments": "Pyridostigmine, IVIG, Immuno modulator",
        "additional": "Avoid infection, Avoid excess strain"
    }
}

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()


        if not (name and age and phone and gender):
            flash("Please fill in all details", "danger")
            return redirect(url_for("register",filename="register.html"))

        try:
            age_int = int(age)
            if not (1 <= age_int <= 117):
                flash("Age is invalid", "danger")
                return redirect(url_for("register",filename="register.html"))
        except ValueError:
            flash("Invalid age format", "danger")
            return redirect(url_for("register",filename="register.html"))

        if len(phone) != 10 or not phone.isdigit():
            flash("Phone number is Invalid", "danger")
            return redirect(url_for("register",filename="register.html"))


        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT Registration_ID FROM Registration WHERE Phone_Number = %s", (phone,))
            existing = cursor.fetchone()
            if existing:
                reg_id = existing[0]
                flash(f"Phone number already registered. Your registration ID is {reg_id}", "info")
            else:
                insert_q = """INSERT INTO Registration (Name, Age, Gender, Phone_Number)
                              VALUES (%s, %s, %s, %s)"""
                cursor.execute(insert_q, (name, age_int, gender, phone))
                conn.commit()
                reg_id = cursor.lastrowid
                flash(f"Registration successful! Your registration ID is {reg_id}", "success")
        except Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass 

        return redirect(url_for("disease"))
    

    return render_template("register.html")



@app.route("/disease", methods=["GET", "POST"])
def disease():
    result = None
    error = None

    try:
        _ = DISEASES
    except NameError:
        print("ERROR: DISEASES not defined in app.py")
        return "Server misconfiguration: DISEASES not defined. Check app.py", 500

    if request.method == "POST":
        name = request.form.get("disease_name", "").strip().lower()
        if name:
            info = DISEASES.get(name)
            if info:
                result = info
            else:
                error = f"No data for '{name}'."
        else:
            error = "Please enter a disease name."

    return render_template("disease.html",
                           DISEASES=DISEASES,
                           result=result,
                           error=error)


@app.route("/diseases")
def diseases():
    names = [f"{i+1}.  {v['title']}" for i, v in enumerate(DISEASES.values())]
    return render_template("diseaselist.html", disease_list=names)

@app.route("/info")
def info():
    info = session.get("disease_info")
    if not info:
        flash("No disease selected", "warning")
        return redirect(url_for("disease"))

    def bullets(text):
        items = [s.strip() for s in text.split(",") if s.strip()]
        return items

    symptoms = bullets(info.get("symptoms", ""))
    investigations = bullets(info.get("investigations", ""))
    treatments = bullets(info.get("treatments", ""))
    additional = bullets(info.get("additional", ""))
    return render_template("info.html", title=info.get("title"),
                           symptoms=symptoms,
                           investigations=investigations,
                           treatments=treatments,
                           additional=additional)


if __name__ == "__main__":
    app.run(debug=True)
