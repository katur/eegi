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
well versus tile | some tables have one, some the other, some both | just use well throughout the database, with accessible Python functions to convert
well names | typically "A01" style, but "A1" for Vidal plates | consistently 3 characters long, except in case of Orfeome clone *name* (see more description in `clones` decisions below).



### `worms` app
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
information about worm strains | no table | `WormStrain` table
referring to worm strains | generally mutant and allele, sometimes just allele | FK to `WormStrain`
par-1 allele | zc310 | zu310

**Decisions to make about `worms` app**
- Rows just inserted by Noah/Katherine into old database accidentally fixed the zc310 error. Could Kris unfix it in GenomeWideGI and GWGI2 (i.e. change zu310 -> zc310 in allele fields and plate names), so that her scoring interface works and so that GenomeWideGI and GWGI2 are consistently wrong?



### `clones` app
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
clone names | sjj\_X and mv\_X | sjj\_X and GHR-X@X
clone mapping info | 1-to-1, scattered over many tables (wherever `clone` is accompanied by `node_primary_name` and/or `gene`) | All mapping isolated to `clones` app, which is connected to rest of database only by FK to `RNAiClone`. Mapping will be 1-to-many.

**Decisions to make about `clones` app**
- The well within GHR-style clones names are "A1" style for GHR-10%, but "A01" style for GHR-11% onward. We should probably leave these as is for the actual clone names, for consistency with the Orfeome database. But in the fields of LibraryWell that refer to vidal clone locations (e.g. the id, and the well column), I'll consistently use "A01" style.
- Are we sure we want RNAiClone instead of Clone prefix for tables?
- Schema for Firoz's tables!



### `library` app
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
plate-level information about library plates | no table | `LibraryPlate` table
well-level clone identities of library plates | `RNAiPlate` (primary plates), `CherryPickRNAiPlate` (secondary) and `ReArrayRNAiPlate` (Julie and Eliana rearrays) | Combine all plates in `LibraryWell`. Do not migrate Julie plates.
well-level parent relationships from primary plates to source plates (i.e., to Ahringer 384 plate or GHR-style Orfeome plates) | can be derived from `RNAiPlate` columns `chromosome`, `384PlateID`, and `384Well` (though confusing because 384PlateID is incomplete without chromosome for Ahringer 384 plates, and because the Orfeome plates are actually 96 wells) | capture with FK from `LibraryWell` to `LibraryWell` 
well-level parent relationships from secondary plates to primary plates | `CherryPickTemplate` (but incomplete; many rows missing) | capture with FK from `LibraryWell` to `LibraryWell`
PK for `LibraryWell` | two fields: plate and well | single field, in format plate\_well (e.g., I-1-A1\_H05)
sequencing results | `SeqPlate` table, which stores mostly conclusions (missing most Genewiz output) | `LibrarySequencing`, which stores mostly Genewiz output

**Decisions to make about `library` app: plate-level**
- Are we sure we want screen level to be captured per experiment, rather than per library plate? If so, Katherine needs to remember to delete screen level from her current LibraryPlate table.
- Should we give the Vidal rearray plates more descriptive names than just integers 1 to 21 (e.g. vidal-1)?
- Should we convert all underscores in plate names to dashes? Already so for Ahringer 384 (e.g. II-4), Ahringer 96 (e.g. II-4-B2), original Orfeome plate (e.g. GHR-10010), proposed Vidal 96 rearray (e.g. vidal-13). Would only need to convert secondary plates (e.g. b1023\_F1) and Eliana rearrays (Eliana\_Rearray\_2). The reason this is nice is so that LibraryWell is more readable (e.g. b1023\_F5\_F05 is confusing).

**Decisions to make about `library` app: well-level**
- Should we add LibraryWell rows to capture wells that supposedly have no clone? Old database does not have these. The reason is that in our copy, sometimes these wells do grow, so even if there is no intended clone it could be determined by sequencing (and actually, some of these did make it into our secondary plates, meaning these plates have no defined parent unless we add these rows).
- Should we really hardcode the intended clone for child plates (instead of relying on pointers)? This has caused database consistency issues in the past.



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
scorer expPeople | only one score ("no bacteria") | convert to hueyling
scorer Julie (MySQL default for scoredBy) | All scores have an improper date, and were probably not added via the traditional scoring interface. All scores are either spn-4 scores (perhaps Julie gave Hueyling at Excel sheet of scores, which might be why Hueyling made "Julie" the default scoredBy), or "no bacteria" scores (which we believe Hueyling and Amelia entered, perhaps using Katherine's growth history data) | convert "no bacteria" scores to hueyling; do not migrate spn-4 scores (these experiments are useless, due to using a reverting spn-4 line)
scorer eliana | some pre-consensus ENH scores | do not migrate eliana's ENH scores (scored before ENH criteria finalized)
scorer lara | some pre-consensus ENH scores | do not migrate lara's ENH scores (scored before ENH criteria finalized)
scorer katy | only pre-consensus ENH scores | do not migrate any katy scores (scored before ENH criteria finalized)
scorer alejandro | only ENH scores | do not migrate any alejandro scores (not well trained, and did not score much)
scorers sherly, giselle, kelly | some pre-consensus ENH scores | migrate in order to investigate relevance of these scores and to ensure all enhancers caught by "real" scorers, but omit from interface

**Decisions to make about `experiments` app: manual scores**
- If real date and time are not known, should I make it null, or just preserve HL's placeholder (i.e. 2011-01-01 00:00:00)?



### `experiments` app: DevStaR scores
**concept** | **GenomeWideGI** | **eegi**
----------- | ---------------- | --------
DevStaR scores table | `RawDataWithScore` | `DevstarScore`

**Decisions to make about `experiments` app: DevStaR scores**
- I'm consistenly using singular for adult, larva, embryo. Is everyone cool with that, or should 'larvae' remain an exception?
- HL used INTEGER for embryo count, embryo per adult, larva per adult. Do we want FLOAT for any of these?
- HL survival/lethality FLOATs seem to truncate at 6 digits past the decimal. Do we want to do this? Easy to just store the real Float.
- HL set embryo per adult and larva per adult to 0 if no adults. Do we want to do this, or should it be null?
- HL also made survival and lethality 0 if no adults, even though adults not used in this equation. Do we want to do this? Why?




### Tables not touched during migration
- attribute, node, synonym (Firoz/mapping domain; he can take info from them if he wants)
- CherryPickList (temporary step in generating CherryPickRNAiPlate; probably meant for deletion)
- CherryPickRNAiPlate\_2011 and CherryPickRNAiPlate\_lock (but ensure they are redundant with CherryPickRNAiPlate)
- ScoreResultsDevStaR (but ensure it is just an incomplete copy of RawDataWithScore, made by Kris)
- PredManualScore and PredManualScoreList (but figure out why these exist!)
- WellToTile (to be replaced with simple Python functions)


-----------------------------------------------------------------------------------
<!--
## Drafts of SQL queries that could be used to bypass the script, if time is a concern

### LibraryPlate (did not exist in GenomeWideGI)

First add 384 plates and Eliana Rearray plates by hand.

Then:

  INSERT INTO LibraryPlate (id, screen\_stage, number\_of\_wells)
  SELECT DISTINCT RNAiPlateID, 1, 96 FROM RNAiPlate;

  INSERT INTO LibraryPlate (id, screen\_stage, number\_of\_wells)
  SELECT DISTINCT RNAiPlateID, 2, 96 FROM CherryPickRNAiPlate;


### Experiment

First correct misspelled allele in eegi.RawData:

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
-->
