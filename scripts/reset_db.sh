echo "yes" | python manage.py flush
find . -path "*/migrations" -not -path "./venv/*"  -exec rm -r {} +
python manage.py makemigrations auth compete judger organization problem submission userprofile
python manage.py migrate
