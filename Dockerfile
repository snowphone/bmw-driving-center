FROM python:slim

ENV TZ=Asia/Seoul

WORKDIR /app


RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry config virtualenvs.in-project false

COPY .                        ./

RUN poetry install --no-dev

ENTRYPOINT [ "python", "/app/bmw_driving_center.py" ]
