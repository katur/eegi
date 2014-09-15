# Database Migration Notes

These notes are about migrating the genome-wide GI project data
from the legacy MySQL database (GenomeWideGI on pleiades)
to the redesigned MySQL database (eegi).

## Data Migration Script

A script is used to migrate new or updated rows;
it does not yet account for deleted rows, 
so should be run on a truncated database just prior to
the official migration to the new database.
The script lives in `utils/management/commands`, and can be run with:

    ./manage.py migrate_legacy_data
    
    
Please see the script's documentation for more information 
(including how to enter legacy database connection information,
optional args, legacy database queries, etc).
But in a nutshell, the script is broken into about 10 steps,
each step roughly corresponding to migrating a single table.
These steps are ordered based on dependencies between steps,
and optional arguments can specify running a subrange of steps.
Within each step, the legacy database is queried
(e.g. to fetch all the rows from some legacy table).
For each row the the query result,
various validation and conversion steps are used to create a Python object
that is compatible with a row in the new database.
Finally, if a corresponding object does not exist in the new database,
the object is saved to the new database;
otherwise, the corresponding object is updated if any changes have occured
since the last migration.

This process of creating a Python object for every single row
(about 4 million rows) is very slow. But it only needs to be run
a few times during development of the new database, and then once 
just prior to the official migration to the new database.
For this reason, its simplicity and robustness was favored over a faster
approach (such as clearing the new database, copying the old tables into the
new database, performing various conversions on the old tables with SQL,
inserting the old rows into the new tables with SQL, and deleting the old
tables).



## Reference of Changes

### general
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
database name | GenomeWideGI | eegi (a la Python package name)
table names | usually CamelCase, but not always | always CamelCase (a la Python class names)
field names | mishmash of under_scores, mixedCase, CamelCase | always underscores (a la Python variables)

### `worms` app
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
information about worm strains | no table | `WormStrain` table
referring to worm strains | generally mutant and allele, sometimes just allele | FK to `WormStrain`
par-1 allele | zc310 | zu310

### `clones` app
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
clone mapping info | 1-to-1, scattered over many tables (wherever `clone` is accompanied by `node_primary_name` and/or `gene`) | All mapping isolated to `clones` app, which is connected to rest of database only by FK to `Clone`. Mapping is 1-to-many.
clone names | sjj\_X and mv\_X | sjj\_X and ???
### `library` app
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
plate-level information about library plates | no table | `LibraryPlate` table
clone locations within library plates | `RNAiPlate` (primary and 384) and `CherryPickRNAiPlate` (secondary) and `ReArrayRNAiPlate` (Julie and Eliana rearrays) | Combine all plates in `LibraryWell`. Do not migrate Julie plates. Still need to decide about Eliana rearrays.
clone parent location relationships | `CherryPickTemplate` (but incomplete, even for secondary rearrays) | capture with FK from `LibraryWell` to `LibraryWell`
sequencing results | `SeqPlate` table, which stores mostly conclusions (missing most Genewiz output) | `LibrarySequencing`, which stores mostly Genewiz output

### `experiments` app: experiments
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
experiments table | `RawData` | `Experiment`
temperature datatype | string (e.g. "25C") | decimal
experiment date datatype | string | date
is\_junk datatype | integer | boolean
is\_junk values | -1 "definite junk", never to be trusted (e.g. wrong worms, wrong bacteria); 1 "possible junk", not up to standards (e.g. temperature slightly off, too many worms per well, bacterial contamination). However, these definitions weren't used consistently. | No separation of possible vs definite junk. Anything untrustworthy should either be deleted (including pictures), or have a comment in the database explaining why it is junk, in order to discourage future consideration (all "definite junk" to date has such a comment, so it is okay to migrate these experiments as generic junk).

### `experiments` app: manual scores
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
manual scores table(s) | `ManualScore` (primary) and `ScoreResultsManual` (secondary) | one table: `ManualScore`
score time datatype | originally int year, string month, int day, string time; scoreYMD eventually added, but incomplete (since not updated by most of HL's programs to add experiments), and doesn't include timestamp | 'aware' datetime
scorer | string of username | FK to `User`
score category -8: secondary pool | was used temporarily to flag 'uncertain' scores. now has no corresponding scores. | do not migrate this category or scores
score category -1: not sure | only Julie scores have this value | do not migrate this category or scores
score category 4: No Larvae | K/S mel-26 scores, for some DevStaR test | do not migrate this category or scores
score category 5: Larvae Present | K/S mel-26 scores, for some DevStaR test | do not migrate this category or scores
score category 6: A lot of Larvae | K/S mel-26 scores, for some DevStaR test (on re-examination, no obvious suppressors, since the L4440 control this week had tons of larvae) | do not migrate this category or scores
score category -6: Poor Image Quality | very old scores only | convert to -7
score category -5: IA Error (i.e., DevStaR issues that aren't caused by poor image quality) | very old scores only | migrate, but omit from interface
scorer expPeople | only one score of "no bacteria" | convert to hueyling
scorer Julie (MySQL default for scoredBy) | All scores have an improper date, and were probably not added via the traditional scoring interface. All scores are either spn-4 scores (perhaps Julie gave Hueyling at Excel sheet of scores, which might be why Hueyling made "Julie" the default scoredBy), or "no bacteria" scores (which we believe Hueyling and Amelia entered, perhaps using Katherine's growth history data) | convert "no bacteria" scores to hueyling; do not migrate spn-4 scores (these experiments are useless, due to using a reverting spn-4 line)
scorer eliana | some pre-consensus ENH scores | do not migrate eliana's ENH scores (scored before ENH criteria finalized)
scorer lara | some pre-consensus ENH scores | do not migrate lara's ENH scores (scored before ENH criteria finalized)
scorer katy | only pre-consensus ENH scores | do not migrate any katy scores (scored before ENH criteria finalized)
scorer alejandro | only ENH scores | do not migrate any alejandro scores (not well trained, and did not score much)
scorers sherly, giselle, kelly | some pre-consensus ENH scores | migrate in order to investigate relevance of these scores and to ensure all enhancers caught by "real" scorers, but omit from interface

### `experiments` app: DevStaR scores
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
DevStaR scores table | `RawDataWithScore` | `DevstarScore`


Still considering these changes
- vidal plate names | e.g. 1 | e.g. vidal-1

Probably not touching these during migration:
- attribute, node, synonym (Firoz/mapping domain)
- WellToTile (to be replaced with simple python functions)
- CherryPickList (temporary step in generating CherryPickRNAiPlate; probably meant for deletion)
- CherryPickRNAiPlate\_2011 and CherryPickRNAiPlate\_lock (but ensure they are redundant with CherryPickRNAiPlate)
- ScoreResultsDevStaR (but ensure it is just an incomplete copy of RawDataWithScore, made by Kris)
- PredManualScore and PredManualScoreList (but figure out why these exist!)


## Possible (untested) SQL queries if you want to not use the script

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
