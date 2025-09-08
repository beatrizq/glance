FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# command to run app.py, which starts the flask development server
CMD ["python", "app.py"]
# command to run gunicorn with my app
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]