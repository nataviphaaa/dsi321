FROM python:3.8

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
COPY . .
CMD ["streamlit", "run", "pgadmin_connect.py"]