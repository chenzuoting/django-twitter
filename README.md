# django-twitter
Terminal 1 (Local):
1. cd /Users/mcfy/Projects/djangoWork/Twitter/django-twitter
2. vagrant up

Terminal 2 (VM):
1. cd /Users/mcfy/Projects/djangoWork/Twitter/django-twitter
2. vagrant ssh
3. cd /vagrant/
4. python manage.py runserver 0.0.0.0:8000 (Can run on pycharm as well)

Git:
1. git status
2. git checkout -b <branch_name>
3. git add .
4. git commit -m "..."
5. git push -u origin <branch_name>
6. git checkout main
7. git pull

DB migration:
1. python manage.py makemigrations
2. python manage.py migrate

Test:
1. Test CMD: In VM: python manage.py test
2. admin / admin
3. testing / testing@testing.com / testing