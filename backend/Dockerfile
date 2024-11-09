FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]