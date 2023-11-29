FROM python:3.10-slim as pv
WORKDIR /movie_model
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health
CMD ["streamlit", "run", "app.py"] 
