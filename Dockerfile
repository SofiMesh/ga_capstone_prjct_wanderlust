FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry
RUN poetry install 


COPY . .
COPY ./pyproject.toml ./poetry.lock*  ./
RUN poetry export -f requirements.txt --output requirements.txt && pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE "wanderlust.settings"
ENV DJANGO_SECRET_KEY "secakljsdfalsdjfai382342"



RUN poetry run python manage.py collectstatic --noinput

CMD poetry run daphne -b 0.0.0.0 -p 8000 wanderlust.asgi:application
