FROM python:3.11.3

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY pyproject.toml $APP_HOME/pyproject.toml
COPY poetry.lock $APP_HOME/poetry.lock

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main
# --no-root --no-dev

COPY . .

RUN pip install flask flask-socketio

EXPOSE 3000

CMD ["python", "main.py"]
