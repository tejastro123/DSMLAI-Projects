from flask import Flask, request, render_template
import joblib
import numpy as np

app = Flask(__name__)

model = joblib.load("models/best_model.pkl")
scaler = joblib.load("models/scaler.pkl")

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    grade = None
    error = None

    if request.method == "POST":
        try:
            study_hours = float(request.form["study_hours"])
            attendance = float(request.form["attendance"])
            participation = float(request.form["participation"])

            if not (0 <= study_hours <= 168):
                error = "Study hours must be between 0 and 168."
            elif not (0 <= attendance <= 100):
                error = "Attendance must be between 0 and 100."
            elif not (0 <= participation <= 10): # Assuming 0-10 scale
                error = "Participation must be between 0 and 10."
            else:
                features = [study_hours, attendance, participation]
                features_scaled = scaler.transform([features])
                prediction = round(model.predict(features_scaled)[0], 2)

                if prediction >= 90:
                    grade = "A"
                elif prediction >= 80:
                    grade = "B"
                elif prediction >= 70:
                    grade = "C"
                elif prediction >= 60:
                    grade = "D"
                else:
                    grade = "F"

        except ValueError:
            error = "Invalid input. Please enter numeric values."

    return render_template("index.html", prediction=prediction, grade=grade, error=error)

if __name__ == "__main__":
    app.run(debug=True)
