@echo off
cd /d "d:\MY-DSMLAI\Projects\Time Series Demand Forecasting System"
call .venv\Scripts\activate
python src\train.py
echo Retaining complete.
