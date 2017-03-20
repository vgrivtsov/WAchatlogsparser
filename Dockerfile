FROM tiangolo/uwsgi-nginx-flask:flask-python3.5-upload
COPY ./app /app
# Add maximum upload of 10 m
RUN rm /etc/nginx/conf.d/upload_100m.conf
COPY upload_10m.conf /etc/nginx/conf.d/



