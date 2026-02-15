from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score
import joblib
from data_preprocessing import load_and_preprocess

X_train, X_test, y_train, y_test = load_and_preprocess("student.csv")

models = {
    "Linear": LinearRegression(),
    "RandomForest": RandomForestRegressor(),
    "GradientBoosting": GradientBoostingRegressor()
}

best_score = -1
best_model = None

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    score = r2_score(y_test, preds)
    print(f"{name} R2: {score}")

    if score > best_score:
        best_score = score
        best_model = model

joblib.dump(best_model, "models/best_model.pkl")
print("Best model saved!")
