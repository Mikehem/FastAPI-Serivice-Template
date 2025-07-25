FROM python:3.7 as base

WORKDIR /home/TEST_Service

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt


RUN pip install xxxai --extra-index-url https://__token__:CR3mfQ-Zsy3QNFzqaz_g@gitlab.com/api/v4/projects/31912870/packages/pypi/simple


# production image.
FROM base as production

WORKDIR /production
RUN apt update
RUN apt install -y poppler-utils
RUN apt install -y tesseract-ocr

COPY . .

ARG PORT=80
ARG HOST=0.0.0.0
ARG APP_MODULE=app.TEST_app:app
ARG WORKERS_PER_CORE=5

ENV MODE=production
ENV CFG_KEY=TEST
ENV CFG_SECRET=KEY
ENV APP_ACRONYM=Secret
ENV APP_MODULE=${APP_MODULE}
ENV WORKERS_PER_CORE=${WORKERS_PER_CORE}
ENV HOST=${HOST}
ENV PORT=${PORT}

EXPOSE ${PORT}

# CMD ["uvicorn", "lrd_fastapi.lrd_app:app", "--host", "0.0.0.0", "--port", "80"]

RUN [ "chmod", "+x", "./scripts/start.sh" ]
ENTRYPOINT [ "./scripts/start.sh" ]

