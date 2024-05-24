FROM python:3.10

ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8080

CMD streamlit run --server.port 8080 --server.enableCORS false main.py