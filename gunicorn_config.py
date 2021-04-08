import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = 'unix:rabbithole.sock'
umask = 0o007
reload = True

#logging
accesslog = '-'
errorlog = '-'