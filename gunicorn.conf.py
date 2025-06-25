# Configuração do Gunicorn para produção
import multiprocessing

# Server socket
bind = "0.0.0.0:5005"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Process naming
proc_name = 'books-api'

# Logging
accesslog = '/var/log/books-api/access.log'
errorlog = '/var/log/books-api/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process ID
pidfile = '/var/run/books-api.pid'

# Daemonize the Gunicorn process (detach & enter background)
daemon = False

# User and group to run as
user = 'www-data'
group = 'www-data'

# Preload app for better performance
preload_app = True