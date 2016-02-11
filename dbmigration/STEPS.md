## Steps to populate an empty database

```
# Migrate the schema
./manage.py migrate


# Sync Clone table
./manage.py import_legacy_database 0 0


# Import mapping data and functional descriptions (both scripts in clones app)
./manage.py import_mapping_data

./manage.py import_functional_descriptions \
  ../materials/functional_descriptions/c_elegans.PRJNA13758.WS240.functional_descriptions.txt


# Sync LibraryPlate table
./manage.py import_legacy_database 1 1


# Sync LibraryStock table, add empty wells, and rerun sync (due to rare case
# of some ElianaRearray wells pointing at empties)
# NOTE: save stderr to manually resolve some legacy stock source ambiguities
./manage.py import_legacy_database 2 2 2> stock1_stderr.out
./manage.py add_empty_library_wells
./manage.py import_legacy_database 2 2 2> stock2_stderr.out

# Do it again just to check
./manage.py import_legacy_database 2 2 2> stock3_stderr.out
./manage.py import_legacy_database 2 2 2> stock4_stderr.out


# Import LEGACY sequencing data
# NOTE: save stderr to manually resolve some legacy ambiguities
./manage.py import_legacy_sequencing_data \
  ../materials/sequencing/tracking_numbers/tracking_numbers_2012.csv \
  ../materials/sequencing/genewiz_dump/genewiz_data 2> seq_stderr.out

# Import more recent sequencing data
./manage.py import_sequencing_data \
  ../materials/sequencing/cherrypick_lists/cherrypick_list_2014.csv \
  ../materials/sequencing/tracking_numbers/tracking_numbers_2014.csv \
  ../materials/sequencing/genewiz_dump/genewiz_data


# Import blat results (library app)
./manage.py import_blat_results ../materials/sequencing/blat_results_from_firoz/joined


# Import WormStrain rows from ../materials/worm_strains/worm_strains.csv
# Import auth_user rows from ../materials/users/users.csv


# Import ExperimentWell and ExperimentPlate
./manage.py import_legacy_database 3 3 2> exp_stderr.out


# Import scores
./manage.py import_legacy_database 4 2> scores_stderr.out


# Manually fix rotated seq plate JL69
# Manually sort out the cherry pick source ambiguities (from paperwork)
# Manually sort out the 4 genewiz migration script errors
```
