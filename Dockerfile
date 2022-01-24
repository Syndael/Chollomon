FROM python:3.8-alpine
ENV TZ=Europe/Madrid

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories

RUN apk update
RUN apk add chromium chromium-chromedriver
RUN apk add tzdata

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./scan.py" ]
