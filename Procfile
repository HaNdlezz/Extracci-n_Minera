web: /home/ubuntu/extraction/bin/gunicorn --access-logfile - --workers 4 --bind unix:/home/ubuntu/extraction/Extraccion_Minera/extraction.sock wsgi:application
worker: python /home/ubuntu/extraction/Extraccion_Minera/manage.py process_tasks --log-std