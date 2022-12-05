FROM python:3.10-bullseye

RUN pip install pipenv

WORKDIR /app
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install

COPY . .

EXPOSE 8080

CMD [ "pipenv", "run", "start"]

