FROM python:3.11-slim AS base
LABEL maintainer="Leonardo Macías Sánchez"

FROM base AS builder
WORKDIR /install
COPY ../requirements /install/requirements

#Instalo las librerias requeridas
RUN pip install --prefix=/install -r requirements/requirements.txt


FROM base
#Para que python no genere archivos de cache (pyc) en el contenedor
ENV PYTHONDONTWRITEBYTECODE 1
#Para que los logs no tengan retardo
ENV PYTHONUNBUFFERED 1
COPY --from=builder /install /usr/local

#Instalo wkhtmltopdf y dependencias
RUN apt-get update && apt-get install -y  --no-install-recommends\
      wkhtmltopdf \
      libqt5webkit5 \
      libqt5printsupport5 \
      libqt5svg5 \
      libqt5widgets5 \
    && rm -rf /var/lib/apt/lists/*

ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf
ENV OPENAI_API_KEY=insert_key

WORKDIR /workdir
COPY ./tutor-app ./tutor-app
COPY ./entrypoint.sh ./entrypoint.sh
RUN mkdir output-reports
#Exponemos el puerto para las comunicaciones con ADARVE
EXPOSE 65431

#Creamos un nuevo usuario con permisos de lectura/escritura/ejecucion en workdir
RUN adduser -u 5678 --disabled-password --gecos "" tutoruser && chown -R tutoruser /workdir && chmod -R 777 /workdir
USER tutoruser

ENTRYPOINT [ "./entrypoint.sh" ]