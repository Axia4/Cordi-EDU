# Cordi-EDU
Cordinación de centros educativos

## Local setup (SQLite + Migrations)

1. Install dependencies:

	pip install -r requirements.txt

2. Initialize migrations (first time):

	flask db init
	flask db migrate -m "Initial"
	flask db upgrade

3. Run the app:

	python main.py

Notes: the app will also create the SQLite file under `_data/db.sqlite3` when started if migrations aren't run.
