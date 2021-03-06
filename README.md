# Genome-Wide Early Embryogenesis Genetic Interactions Project

Django web interface and programs for a genome-wide
*Caenorhabditis elegans* screen, which used millions of pairwise gene
knockdown experiments to uncover suppressor and enhancer phenotypes to
reveal genetic interactions.

1. [Code](#code)
2. [Apps](#apps)
3. [Database](#database)
4. [Installation](#installation)


## Code

The project is organized the standard
[Django](https://www.djangoproject.com/) way, with most code in Python.

Python version is listed in [runtime.txt](runtime.txt).
Python package dependencies, including Django,
are listed in [requirements.txt](requirements.txt).

HTML is in the
[Django template language](https://docs.djangoproject.com/en/dev/topics/templates/).

Javascript uses [jQuery](http://jquery.com/).

CSS is in [SASS](http://sass-lang.com/).
[gulpfile.js](gulpfile.js) can be used to automate the compilation of
SASS while in development. The package dependencies for using Gulp are
listed in [package.json](package.json). Please see
[INSTALL.md](https://github.com/katur/eegi/blob/master/INSTALL.md#cssjavascript-dependencies)
for more details on how to install these dependencies and use this script.

Managerial scripts live in the standard Django location:
`appname/management/commands/scriptname.py`, to be run with
`./manage.py scriptname`.

To browse these scripts, run `./manage.py help`.
For help on a particular script, run `./manage.py help scriptname`.


## Apps

The project is organized into four Django apps centered around the project
data:

- [worms](worms) captures the *C. elegans* strains used in the screen.
- [clones](clones) captures the RNAi feeding clones used in the screen,
  including information about what genes these clones target.
- [library](library) captures the physical RNAi stocks used in the screen,
  including sequencing results.
- [experiments](experiments) captures the actual experiments, including
  human and machine scores of results.


One other Django app holds simple website functionality used across the
other apps:

- [website](website) holds website functionality that does not fall into
  one of the other apps
  (e.g., the templates and stylesheets for the home page, footer, etc)


Finally, an explanation of some other top-level directories:

- [utils](utils) holds some very general helper functions
- [antiquated](antiquated) holds some old code that predates this Django project
- [dbmigration](dbmigration) holds the functionality for syncing the database
  from the legacy database. This was a Django app, but is now de-activated.


## Database

[Click here](https://www.lucidchart.com/documents/view/18217c4a-69c6-44f8-bf4f-0acf15e28973)
to view the database schema on Lucidchart
(or [here](https://www.lucidchart.com/publicSegments/view/a3361480-4c9a-43ba-8be5-84f798391cef/image.pdf)
to download a PDF).

[Click here](https://www.lucidchart.com/documents/view/b63066e2-0f57-4d04-a828-65cf62bf1bb0)
to view the old, plate-level database schema on Lucidchart
(or [here](https://www.lucidchart.com/publicSegments/view/85dfbf91-11fd-4afa-9392-84d26330b648/image.pdf)
to download a PDF).

[Click here](https://www.lucidchart.com/documents/view/aa16dc41-3f3f-4944-bc5b-982697bb8ba9)
to view Firoz's clone mapping database schema on Lucidchart
(or [here](https://www.lucidchart.com/publicSegments/view/84b7950c-3e2c-4446-a954-47208a38d098/image.pdf)
to download a PDF).

Notes on migrating the data from the old database
(`GenomeWideGI` on pleiades)
are in [dbmigration/README.md](dbmigration/README.md).


## Installation

See [INSTALL.md](INSTALL.md).
