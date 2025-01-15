FROM python:latest

RUN pip install --upgrade pip poetry

WORKDIR /code
COPY . .

RUN poetry install --without dev

ENTRYPOINT ["poetry", "run", "tatl"]
