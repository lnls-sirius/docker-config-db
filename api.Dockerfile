FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./api_requirements.txt /requirements.txt

RUN echo nameserver 10.0.0.71 >> /etc/resolv.conf && \
      pip install -r /requirements.txt

COPY ./app /app
