bind = '0.0.0.0:8080'
backlog = 2048
workers = 3
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 5
spew = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
daemon = False
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
proc_name = None
#clean up those pesky health checks
logger_class = 'conf.classy_logger.CustomGunicornLogger'
forwarded_allow_ips="*"


#Ignore health checks
def pre_request(worker, req):
    if req.path == '/health':
        return
    worker.log.debug("%s %s" % (req.method, req.path))
