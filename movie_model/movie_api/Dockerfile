FROM python:3.10-slim as pv
WORKDIR /movie_model
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .
EXPOSE 80
CMD ["uvicorn", "main:app"]
 #,"--host", "127.0.0.1", "--port", "8000"]

