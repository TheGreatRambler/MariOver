FROM python:3.8

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN python3 generate_console_data.py

CMD ["uvicorn", "mariover:app", "--port", "9876", "--host", "0.0.0.0"]