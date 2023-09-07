FROM python:3.10-slim
RUN apt-get update 
RUN apt-get install -y gettext
RUN apt-get install -y telnet
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r ./requirements.txt --no-cache-dir
COPY . .
EXPOSE 465
CMD ["gunicorn", "marketgraphicimages.wsgi:application", "--bind", "0:8000" ]