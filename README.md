# Genome-Wide EEGI (Early Embryogenesis Genetic Interactions) Project

Django-based web interface and programs for a genome-wide *C. elegans* screen,
which used millions of pairwise gene knockdown experiments to uncover
suppressor and enhancer phenotypes to reveal genetic interactions.


## Dependencies

Python version is listed in `runtime.txt`.

Package dependencies are listed in `requirements.txt`.


## Database

The database is MySQL, named eegi.

[Here](https://www.lucidchart.com/documents/view/4eb4bac8-5339-ae33-8c00-5ccd0a0085f4)
is a web view of the database schema on Lucidchart.

[Here](https://www.lucidchart.com/publicSegments/view/53f3c896-8854-49cc-8c3a-69d30a005381)
is a the same view as a pdf.

Notes on migrating the data from Huey-Ling's MySQL database
(`GenomeWideGI` on `pleiades.bio.nyu.edu`)
are in `database_migration_notes.md`.

## Apps

The project is organized into four apps.

`worms` captures the *C. elegans* strains used in the screen.

`library` captures the physical RNAi stocks used in the screen,
including sequencing results off these plates.

`clones` captures the theoretical identity of the RNAi clones,
including mapping information.

`experiments` captures the experiments (each a worm combined with an RNAi
library plate),
including human and machine scores derived from these experiments.


## Code

The project is organized in the standard
[Django](https://www.djangoproject.com/) way, with almost all code in Python.

HTML uses the
[Django template language](https://docs.djangoproject.com/en/dev/topics/templates/).

CSS is in [SASS](http://sass-lang.com/). Run
`sass -wc --style compressed website/static/website/stylesheets/styles.sass`
to compile.

Javascript is in [jQuery](http://jquery.com/).

Purely offline, managerial scripts (e.g. to process data)
live in the standard location: `appname/management/commands/scriptname.py`,
in order to be run as `./manage.py scriptname`.
