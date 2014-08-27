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


# Code
CSS is in [SASS](http://sass-lang.com/). Run
`sass -wc --style compressed website/static/website/stylesheets/styles.sass`
to compile.

Javascript is in [jQuery](http://jquery.com/).
