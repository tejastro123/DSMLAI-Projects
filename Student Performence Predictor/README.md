# Student Performance Predictor

## Setup & Run

1. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

1. **Train Models**
    * *Note: This dataset is large (1M rows). Training RandomForest and GradientBoosting may take 5-10 minutes.*

    ```bash
    py src/train.py
    ```

    (Use `python` instead of `py` if that is your default).

1. **Run Application**

    ```bash
    py app/app.py
    ```

    Access the app at: <http://127.0.0.1:5000>

## Features

* **UI**: Dark theme with responsive design.

* **Input Validation**: Ensures study hours, attendance, and participation are within logical ranges.

* **Grade Estimation**: Automatically estimates a letter grade (A-F) based on the predicted score.
