# Database Migration Notes

These notes are about migrating the genome-wide GI project data
from the legacy MySQL database (GenomeWideGI on pleiades)
to the redesigned MySQL database (eegi).

## Data Migration Script

A script is used to migrate new or updated rows,
which lives in `utils/management/commands`. To run:

    ./manage.py migrate_legacy_data

The script does not yet account for deleted rows. So when we are ready
to officially migrate to the new database, the new database should be
populated from scratch in order to account for deleted rows.

In a nutshell, the script is broken into steps,
where each step roughly corresponds to a database table.
These steps are ordered based on dependencies between steps,
and optional arguments can specify running a subrange of steps.
Within each step, the legacy database is queried
(e.g. to fetch all the rows from some legacy table).
For each row the the query result,
various validation and conversion steps are used to create a Python object
that is compatible with a row in the new database.
Finally, if a corresponding object does not exist in the new database,
the object is saved to the new database;
otherwise, the corresponding object is updated if any updates have occured.

This process of creating a Python object for every single row
(about 4 million rows) is very slow. But it only needs to be run
periodically during development of the new database, and then once
prior to the official migration to the new database.
For this reason, its simplicity and robustness was favored over a faster
approach (such as clearing the new database, copying the old tables into the
new database, performing various conversions on the old tables with SQL,
inserting the old rows into the new tables with SQL, and deleting the old
tables).

Find further documentation in the script itself (including which queries were
performed on the legacy database).
But below is a quick list of changes that were made between the old and
new database.


## Reference of Changes

*concept* | *GenomeWideGI* | *eegi*
--------- | -------------- | ------
information about worm strains | no table | `WormStrain` table
referring to worm strains | generally mutant and allele, sometimes just allele | FK to `WormStrain`
plate-level information about library plates | no table | `LibraryPlate` table
clone locations within library plates | `RNAiPlate` (primary) and `CherryPickRNAiPlate` (secondary) and `ReArrayRNAiPlate` (Julie and Eliana rearrays) | combine in `LibraryWell`; do not migrate Julie plates; still need to decide about Eliana Rearrays
clone parent location relationships | `CherryPickTemplate` (incomplete) | capture in `LibraryWell`
sequencing results: table name | `SeqPlate` | `LibrarySequencing`
sequencing results: what information is stored | mostly conclusions, hardly any Genewiz output | raw Genewiz output
clone mapping info | 1-to-1 scattered, 1-to-many in | 1-to-many `CloneMapping` table
experiments table | `RawData` | `Experiment`
temperature datatype | string (e.g. "25C") | decimal
experiment date datatype | string | date
human scores table(s) | `ManualScore` (primary) and `ScoreResultsManual` (secondary) | one table: `ManualScore`
score time datatype | originally int year, string month, int day, string time; scoreYMD incomplete | 'aware' datetime
scorer | string of username | FK to `User`
score category -8: secondary pool | no corresponding scores | no not migrate category or scores
score category -1: not sure | only Julie sscores | do not migrate category or scores
score category 4: No Larvae | K/S mel-26 scores for test | do not migrate category or scores
score category 5: Larvae Present | K/S mel-26 scores for test | do not migrate category or scores
score category 6: A lot of Larvae | K/S mel-26 scores for test (no obvious suppressors) | do not migrate category or scores
score category -6: Poor Image Quality | very old scores only | convert to -7 (problem)
score category -5: IA Error | very old scores only | migrate, but omit from interface
scorer expPeople | only one NB score | convert to hueyling
scorer Julie (MySQL default) | spn-4 scores and -2 (NB) scores | convert NB scores to hueyling; do not migrate spn-4 scores (useless)
scorer alejandro | all ENH scores | do not migrate any alejandro scores
scorer katy | all ENH scores | do not migrate any katy scores
scorer eliana | pre-consensus ENH scores | do not migrate eliana's ENH scores
scorer lara | pre-consensus ENH scores | do not migrate lara's ENH scores
scorers sherly, giselle, kelly | pre-consensus ENH scores | migrate, but omit from interface (to investigate relevance)
DevStaR scores table | `RawDataWithScore` | `DevstarScore`


Still considering these changes
- vidal plate names | e.g. 1 | e.g. vidal-1

Probably not touching these during migration:
- attribute, node, synonym (Firoz domain)
- WellToTile (to be replaced with simple python functions)
- CherryPickList (temporary step in generating CherryPickRNAiPlate; probably meant for deletion)
- CherryPickRNAiPlate\_2011 and CherryPickRNAiPlate\_lock (but ensure they are redundant with CherryPickRNAiPlate)
- ScoreResultsDevStaR (but ensure it is just an incomplete copy of RawDataWithScore, made by Kris)
- PredManualScore and PredManualScoreList (but figure out why these exist!)


## Draft of SQL queries for a faster approach

### WormStrain (did not exist in GenomeWideGI)
Add by hand, referencing Google Doc

### LibraryPlate (did not exist in GenomeWideGI)
Add 384 plates and Eliana Rearray plates by hand.

Then:

  INSERT INTO LibraryPlate (id, screen_stage, number_of_wells)
  SELECT DISTINCT RNAiPlateID, 1, 96 FROM RNAiPlate;

  INSERT INTO LibraryPlate (id, screen_stage, number_of_wells)
  SELECT DISTINCT RNAiPlateID, 2, 96 FROM CherryPickRNAiPlate;


### Experiment
Correct misspelled allele in eegi.RawData:

    UPDATE RawData SET mutantAllele='zu310' WHERE mutantAllele='zc310';

Temporarily set eegi.WormStrain.gene to 'N2' for N2, in order for join to work
(the old database had N2 listed as a mutation).

Then:

    INSERT INTO Experiment
    SELECT expID, WormStrain.name, LibraryPlate.name,
        CAST(SUBSTRING_INDEX(temperature, 'C', 1) AS DECIMAL(3,1)),
        CAST(recordDate AS DATE), ABS(isJunk), comment
    FROM RawData
    LEFT JOIN WormStrain
    ON RawData.mutant = WormStrain.gene
    AND RawData.mutantAllele = WormStrain.allele
    LEFT JOIN LibraryPlate
    ON RawData.RNAiPlateID = LibraryPlate.name
    WHERE (expID < 40000 OR expID > 49999)
    AND RNAiPlateID NOT LIKE "Julie%";
