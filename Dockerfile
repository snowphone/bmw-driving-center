FROM python:slim

ENV TZ=Asia/Seoul

WORKDIR /app


RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry config virtualenvs.in-project false

COPY pyproject.toml             ./
COPY src                        ./src/

RUN poetry install --no-dev

ENTRYPOINT [ "python", "/app/src/bmw_driving_center.py" ]
