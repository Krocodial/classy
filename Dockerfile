FROM python:3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home --shell /bin/bash classy
COPY . /home/classy
RUN chown -R classy:classy /home/classy 
USER classy
WORKDIR /home/classy
#RUN python manage.py collectstatic --noinput
#RUN chmod -R +r conf
RUN python manage.py collectstatic --noinput
RUN chmod -R +r conf


CMD python manage.py migrate && python manage.py createcachetable && python manage.py check && gunicorn --bind 0.0.0.0:8080 wsgi

#docker build --no-cache -t classy .
#docker run -p 0.0.0.0:8080:8080 --env-file .env classy


