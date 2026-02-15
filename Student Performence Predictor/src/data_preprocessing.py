import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

def load_and_preprocess(path):
    df = pd.read_csv(path)

    # Example target
    target = "total_score"

    # Handle missing values
    df.fillna(df.median(numeric_only=True), inplace=True)

    # Encode categorical columns
    le = LabelEncoder()
    for col in df.select_dtypes(include="object").columns:
        df[col] = le.fit_transform(df[col])

    X = df.drop([target, "student_id", "grade"], axis=1)
    y = df[target]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    joblib.dump(scaler, "models/scaler.pkl")

    return train_test_split(X_scaled, y, test_size=0.2, random_state=42)
