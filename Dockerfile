FROM python:3.9
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ['python3', 'main.py']