FROM python:3.11.5

WORKDIR /api

COPY . /api

RUN pip install -r requirements.txt

CMD uvicorn main:app --port=8000 --host=0.0.0.0