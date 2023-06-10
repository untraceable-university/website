FROM python:3.11.4
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y && \
 apt-get install --auto-remove -y \
   gettext locales
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
