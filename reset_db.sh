echo "yes" | python manage.py flush
find . -path "*/migrations" -not -path "./venv/*"  -exec rm -r {} +
rm db.sqlite3
python manage.py makemigrations auth compete judger organization problem submission userprofile
python manage.py migrate