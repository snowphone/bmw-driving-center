FROM python:slim

ENV TZ=Asia/Seoul

WORKDIR /app


RUN apt-get update && \
	rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry config virtualenvs.in-project false

ENV DRIVER_FILE=bmw_driving_center.py

COPY pyproject.toml             ./
COPY "${DRIVER_FILE}"           ./

RUN poetry install --no-dev

ENTRYPOINT [ "python", /app/bmw_driving_center.py ]
