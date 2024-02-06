FROM python:3

WORKDIR /app

RUN pip install -IU pip setuptools wheel

COPY requirements.txt .

RUN pip install -IUr requirements.txt

COPY main.py .

CMD ./main.py
