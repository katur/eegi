# Genome-Wide Early Embryogenesis Genetic Interactions Project

Django-based web interface and programs for a genome-wide
*Caenorhabditis elegans* screen, which used millions of pairwise gene
knockdown experiments to uncover suppressor and enhancer phenotypes to
reveal genetic interactions.


## Installation

See [INSTALL.md](INSTALL.md) for sample Ubuntu deployment steps.


## Dependencies

Python version is listed in [runtime.txt](runtime.txt).

Package dependencies, including Django itself,
are listed in [requirements.txt](requirements.txt).
These should be [pip](https://pypi.python.org/pypi/pip)-installed into a fresh
[Python virtual environment](http://virtualenv.readthedocs.org/)
wherever the project runs (for development or production). I use
[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)
to make working with Python virtual environments easier.

In a nutshell (assuming pip, virtualenv, and virtualenvwrapper already
installed):

```
mkvirtualenv eegi
workon eegi
pip install -r requirements.txt
```


## Database

The database is MySQL, and is named `eegi`.

[Here](https://www.lucidchart.com/documents/view/4eb4bac8-5339-ae33-8c00-5ccd0a0085f4)
is a web view of the database schema on Lucidchart
([here](https://www.lucidchart.com/publicSegments/view/53f3c896-8854-49cc-8c3a-69d30a005381)
as a pdf).

[Here](https://www.lucidchart.com/documents/view/819feb06-fb91-4262-8f39-aa8584e6c02b)
is the schema for Firoz's clone mapping database, related to this project.

Notes on migrating the data from the old database
(`GenomeWideGI` on pleiades)
are in [dbmigration/README.md](dbmigration/README.md).


## Apps

The project is organized into four main apps centered around the project data:

- [worms](worms) captures the *C. elegans* strains used in the screen.
- [clones](clones) captures the RNAi feeding clones used in the screen,
including information about what genes these clones target.
- [library](library) captures the physical RNAi stocks used in the screen,
including sequencing results.
- [experiments](experiments) captures the actual experiments, including
human and machine scores of results.


There are several other, organizational apps:

- [website](website) holds aspects of the website that are common to all apps (e.g.,
the templates and stylesheets for the home page, footer, etc)
- [dbmigration](dbmigration) holds the functionality for syncing the database according to
the legacy database


Finally, an explanation of these top level directories (which are not apps):

- [utils](utils) holds a few very general helper functions
- `materials`, excluded from the repo, holds various input files (Genewiz
sequencing output, the official Ahringer RNAi library Excel database, etc.)
- `backups`, excluded from the repo, holds MySQL database backups, schema
backups, etc.
- [antiquated](antiquated) holds older code that predates this Django project


## Code

The project is organized the standard
[Django](https://www.djangoproject.com/) way, with most code in Python.

HTML is in the
[Django template language](https://docs.djangoproject.com/en/dev/topics/templates/).

CSS is in [SASS](http://sass-lang.com/). Run
`sass --compile --style compressed website/static/stylesheets/styles.sass`
to compile (assuming sass is installed).

Javascript is in [CoffeeScript](http://coffeescript.org/). Run
`coffee --compile website/static/js/*.coffee`
to compile (assuming coffee is installed).

Instead of compiling the SASS and CoffeeScript separately,
feel free to use the [Gulp.js build script](gulpfile.js),
run simply with `gulp`.

To set up the project for gulping (assuming [Gulp.js](http://gulpjs.com/)
is installed on the system), run the following in the project root
to install project-specific gulp packages in a git-ignored directory called
`node_modules`:

```
npm install --dev-save gulp
npm install --dev-save gulp-util
npm install --dev-save gulp-plumber
npm install --dev-save gulp-ruby-sass
npm install --dev-save gulp-coffee
```

Managerial scripts
(e.g. the script that migrates data from the old database)
live in the standard location: `appname/management/commands/scriptname.py`,
to be run with `./manage.py scriptname`. To browse these scripts,
run `./manage.py help`.
