## Steps to populate an empty database

```
# Migrate the schema
./manage.py migrate

# Sync Clone table
./manage.py import_legacy_database 0 0

# Import mapping data and functional descriptions (both scripts in clones app)
./manage.py import_mapping_data
./manage.py import_functional_descriptions materials/functional_descriptions/c_elegans.PRJNA13758.WS240.functional_descriptions.txt

# Sync LibraryPlate table
./manage.py import_legacy_database 1 1

# Sync LibraryStock table, add empty wells, and rerun sync (due to rare case
# of some ElianaRearray wells pointing at empties)
./manage.py import_legacy_database 2 2
./manage.py add_empty_library_wells
./manage.py import_legacy_database 2 2

# Import sequencing data (dbmigration app) and blat results (library app)
./manage.py import_legacy_genewiz_data materials/sequencing/genewiz/tracking_numbers.csv materials/sequencing/genewiz/genewiz_data
./manage.py import_blat_results materials/sequencing/blat_results_from_firoz/joined

# Import WormStrain rows from materials/worm_strains/worm_strains.csv
# Import auth_user rows from materials/users/users.csv

# Import ExperimentWell and ExperimentPlate
./manage.py import_legacy_database 3 3 2> stderr.out

# Import scores
./manage.py import_legacy_database 4
```
