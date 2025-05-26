import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 1  # Use only 1 worker for GPU models to avoid VRAM conflicts
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for long audio files
keepalive = 2
max_requests = 100
max_requests_jitter = 10

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'whisperx-api'

# Memory management
preload_app = True
enable_stdio_inheritance = True

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    server.log.info("WhisperX API Server is ready. Listening on: %s", server.address)

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
