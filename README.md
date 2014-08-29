# Genome-Wide EEGI (Early Embryogenesis Genetic Interactions) Project

Django-based web interface and programs for a genome-wide *C. elegans* screen,
which used millions of pairwise gene knockdown experiments to uncover
suppressor and enhancer phenotypes to reveal genetic interactions.


## Database

The database is MySQL, and is named `eegi`.

[Here](https://www.lucidchart.com/documents/view/4eb4bac8-5339-ae33-8c00-5ccd0a0085f4)
is a web view of the database schema on Lucidchart.

[Here](https://www.lucidchart.com/publicSegments/view/53f3c896-8854-49cc-8c3a-69d30a005381)
is a the same schema view as a pdf.

Notes on migrating the data from Huey-Ling's MySQL database
(`GenomeWideGI` on pleiades)
are in `database_migration_notes.md`.


## Dependencies

Python version is listed in `runtime.txt`.

Package dependencies, including Django itself,
are listed in `requirements.txt`.
These should be [pip](https://pypi.python.org/pypi/pip)-installed into a fresh
[Python virtual environment](http://virtualenv.readthedocs.org/)
wherever the project runs (for development or production).
I use
[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)
to make working with Python virtual environments easier.

In a nutshell (assuming pip, virtualenv, and virtualenvwrapper already
installed):

    mkvirtualenv eegi
    workon eegi
    pip install -r requirements.txt


## Apps

The project is organized into four data-oriented apps.

`worms` captures the *C. elegans* strains used in the screen.

`clones` captures the theoretical identity of the RNAi clones,
including mapping information.

`library` captures the physical RNAi stocks used in the screen,
including sequencing results.

`experiments` captures the actual experiments,
including human and machine scores of results.

There is also an app `website` for aspects of the website that are common
between apps.

There is also an app `utils` for utilities shared by all apps.


## Code

The project is organized in the standard
[Django](https://www.djangoproject.com/) way, with almost all code in Python.

HTML uses the
[Django template language](https://docs.djangoproject.com/en/dev/topics/templates/).

CSS is in [SASS](http://sass-lang.com/). Run
`sass -wc --style compressed website/static/website/stylesheets/styles.sass`
to compile.

Javascript is in [jQuery](http://jquery.com/).

Purely offline scripts to be run by the project maintainer
(e.g. to migrate data from the old database)
live in the standard location: `appname/management/commands/scriptname.py`,
to be run with `./manage.py scriptname`.
