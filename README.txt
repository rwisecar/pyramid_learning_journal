learning_journal README
==================

Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/pip install -e .

- $VENV/bin/initialize_learning_journal_db development.ini

- $VENV/bin/pserve development.ini

This is blog app made using Pyramid and SQLAlchemy, which will hold learning journal entries.

It is deployed on Heroku at: https://pyramid-blog.herokuapp.com/