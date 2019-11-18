FROM python:3

COPY . /opt/app-root/
WORKDIR /opt/app-root

RUN pip install --no-cache-dir -r requirements.txt 
#    apt-get update && apt-get -y install cron

#useradd --gid 0 --create-home --shell /bin/bash classy && \

#COPY crontab/classy /etc/cron.d/
#COPY . /home/classy
RUN chown -R 1001:0 /opt/app-root 
    #chmod 0644 /etc/cron.d/classy && \
    #crontab /etc/cron.d/classy && \
    #touch /var/log/cron.log && \
    #chmod 544 /var/log/cron.log && \
    #touch /etc/crontab /etc/cron.*/* 

#RUN update-rc.d cron defaults
#USER classy

#RUN python manage.py collectstatic --noinput
#RUN chmod -R +r conf


#COPY crontab/entrypoint /entrypoint
#RUN chmod +x /entrypoint
#ENTRYPOINT ["/entrypoint"]

USER 1001

CMD python manage.py migrate && python manage.py createcachetable && python manage.py check && gunicorn --bind 0.0.0.0:8080 --access-logfile - --error-logfile - --access-logformat "'%({x-forwarded-for}i)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'" --forwarded-allow-ips "*" -c conf/gunicorn.py --timeout 300 -w 3 --threads 4 --keep-alive 10 --graceful-timeout 300 wsgi

#docker build --no-cache -t classy .
#docker run -p 0.0.0.0:8080:8080 --env-file .env classy


