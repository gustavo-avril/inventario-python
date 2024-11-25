# Usa una imagen base de Python
FROM tiangolo/uwsgi-nginx-flask:python3.8

# Copia tu aplicación y archivos necesarios
COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt
COPY ./templates /app/templates
COPY ./static /app/static
COPY ./uwsgi.ini /app/uwsgi.ini

# Instala wkhtmltopdf y las dependencias de Python
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && pip install --no-cache-dir -r /app/requirements.txt

# Comando para iniciar la aplicación
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]