FROM python:3.4

RUN apt-get update && apt-get install -y --no-install-recommends librrd-dev net-tools \
        && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
ADD . /usr/src/app

RUN python manage.py migrate

RUN pip install --no-cache-dir honcho
CMD ["honcho", "start"]

