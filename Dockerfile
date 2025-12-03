FROM python:3.12

ARG APP_GID=1000
ARG APP_UID=1000
ARG APP_HOME=/home/app

RUN python3 -m pip install poetry==1.8.4

RUN groupadd --gid $APP_GID app
RUN useradd --uid $APP_UID --gid app --shell /bin/bash -d $APP_HOME app
RUN mkdir -p $APP_HOME && chown app:app $APP_HOME

USER app
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.path $APP_HOME/venv
RUN poetry install --no-root
