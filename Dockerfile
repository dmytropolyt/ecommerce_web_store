FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app

WORKDIR /app

EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client nodejs npm jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base gcc postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static

RUN cd frontend && \
    npm install && \
    npm run build

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PATH="/scripts:/py/bin:$PATH"

ENTRYPOINT ["/app/entrypoint.sh"]