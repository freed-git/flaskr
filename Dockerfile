FROM python:3.8-slim-buster

ENV FLASK_APP=flaskr
ENV FLASK_ENV=development
ENV OTEL_PYTHON_LOG_CORRELATION=true

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "flask" ]

CMD [ "run", "--host", "0.0.0.0" ]

# ENTRYPOINT [ "waitress-serve" ]

# CMD [ "--call", "flaskr:create_app" ]
