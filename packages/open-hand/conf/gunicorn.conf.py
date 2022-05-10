from os import environ


environ["env"] = "dev"
# environ["SCRIPT_NAME"] = "/service"
chdir = "src"
wsgi_app = "web:create_app()"
bind = "0.0.0.0:8000"

loglevel = "debug"

workers = 2

# access_log_format                 = %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"
# accesslog                         = None
# backlog                           = 2048
# bind                              = ['0.0.0.0:8000']
# ca_certs                          = None
# capture_output                    = False
# cert_reqs                         = 0
# certfile                          = None
# check_config                      = False
# child_exit                        = <ChildExit.child_exit()>
# ciphers                           = None
# config                            = conf/gunicorn.conf.py
# daemon                            = False
# default_proc_name                 = gunicorn
# disable_redirect_access_to_syslog = False
# do_handshake_on_connect           = False
# dogstatsd_tags                    =
# enable_stdio_inheritance          = False
# errorlog                          = -
# forwarded_allow_ips               = ['127.0.0.1']
# graceful_timeout                  = 30
# group                             = 1000
# initgroups                        = False
# keepalive                         = 2
# keyfile                           = None
# limit_request_field_size          = 8190
# limit_request_fields              = 100
# limit_request_line                = 4094
# logconfig                         = None
# logconfig_dict                    = {}
# logger_class                      = gunicorn.glogging.Logger
# max_requests                      = 0
# max_requests_jitter               = 0
# nworkers_changed                  = <NumWorkersChanged.nworkers_changed()>
# on_exit                           = <OnExit.on_exit()>
# on_reload                         = <OnReload.on_reload()>
# on_starting                       = <OnStarting.on_starting()>
# paste                             = None
# pidfile                           = None
# post_fork                         = <Postfork.post_fork()>
# post_request                      = <PostRequest.post_request()>
# post_worker_init                  = <PostWorkerInit.post_worker_init()>
# pre_exec                          = <PreExec.pre_exec()>
# pre_fork                          = <Prefork.pre_fork()>
# pre_request                       = <PreRequest.pre_request()>
# preload_app                       = False
# print_config                      = True
# proc_name                         = None
# proxy_allow_ips                   = ['127.0.0.1']
# proxy_protocol                    = False
# pythonpath                        = None
# raw_env                           = []
# raw_paste_global_conf             = []
# reload                            = False
# reload_engine                     = auto
# reload_extra_files                = []
# reuse_port                        = False
# secure_scheme_headers             = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}
# sendfile                          = None
# spew                              = False
# ssl_version                       = 2
# statsd_host                       = None
# statsd_prefix                     =
# strip_header_spaces               = False
# suppress_ragged_eofs              = True
# syslog                            = False
# syslog_addr                       = udp://localhost:514
# syslog_facility                   = user
# syslog_prefix                     = None
# threads                           = 1
# timeout                           = 30
# tmp_upload_dir                    = None
# umask                             = 0
# user                              = 1000
# when_ready                        = <WhenReady.when_ready()>
# worker_abort                      = <WorkerAbort.worker_abort()>
# worker_class                      = sync
# worker_connections                = 1000
# worker_exit                       = <WorkerExit.worker_exit()>
# worker_int                        = <WorkerInt.worker_int()>
# worker_tmp_dir                    = None
# wsgi_app                          = web:create_app()
