# import streamlit as st
# import joblib
# import numpy as np

# model = joblib.load("nephritis_model.pkl")

# st.title("Nephritis Prediction System")

# features = []
# for col in range(6):
#     val = st.number_input(f"Feature {col+1}", value=0)
#     features.append(val)

# if st.button("Predict"):
#     prediction = model.predict([features])[0]
#     if prediction == 1:
#         st.error("High Risk of Nephritis")
#     else:
#         st.success("Low Risk")

import streamlit as st
import joblib
import numpy as np

# Load trained model
model = joblib.load("nephritis_model.pkl")

st.set_page_config(page_title="Nephritis Prediction", layout="centered")

st.title("Nephritis Prediction System")
st.write("Enter patient symptoms to predict the risk of nephritis.")

st.markdown("---")

# Feature Inputs (based on dataset)
temperature = st.number_input("Temperature", min_value=35.0, max_value=42.0, value=37.0)

nausea = st.selectbox("Nausea", ["No", "Yes"])
lumbar_pain = st.selectbox("Lumbar Pain", ["No", "Yes"])
urine_pushing = st.selectbox("Urine Pushing", ["No", "Yes"])
micturition_pain = st.selectbox("Micturition Pain", ["No", "Yes"])
burning = st.selectbox("Burning of Urethra", ["No", "Yes"])
inflammation = st.selectbox("Inflammation", ["No", "Yes"])

# Convert Yes/No to 0/1
def encode(value):
    return 1 if value == "Yes" else 0

features = np.array([[
    temperature,
    encode(nausea),
    encode(lumbar_pain),
    encode(urine_pushing),
    encode(micturition_pain),
    encode(burning),
    encode(inflammation)
]])

st.markdown("---")

if st.button("Predict"):
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    if prediction == 1:
        st.error(f"High Risk of Nephritis (Probability: {probability:.2f})")
    else:
        st.success(f"Low Risk of Nephritis (Probability: {probability:.2f})")
