# Database Migration Notes

## General Description

These notes are about migrating the genome-wide GI project data
from the legacy MySQL database (GenomeWideGI on pleiades)
to the redesigned MySQL database (eegi).

A script is used to migrate new or updated rows,
which lives in `utils/management/commands`. To run it:
    `./manage.py migrate_legacy_data`.

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
tables). See untested example queries in last section of this document.

For precise details about the steps (including legacy queries performed,
rules regarding data that might not be pulled, etc), please see the script
itself.
But below is a quick list of changes that were made between the old and
new database.


## Change Reference


*concept* | *GenomeWideGI* | *eegi*
---------   --------------   ------
worm strain information | no table | `WormStrain` table
plate-level experiment information | `RawData` | `Experiment`
plate-level library plates | no table | `LibraryPlate` table
human scores | `ManualScore` (primary) and `ScoreResultsManual` (secondary) | one table: `ManualScore`
DevStaR scores | `RawDataWithScore` | `DevstarScore`
clone location in plates | `RNAiPlate` (primary) and `CherryPickRNAiPlate` (secondary) | combine in `LibraryWell`
clone parent location relationships | `CherryPickTemplate` (incomplete) | capture in `LibraryWell`
sequencing result table name | `SeqPlate` | `LibrarySequencing`
sequencing result info stored | mostly conclusions, hardly any Genewiz output | raw Genewiz output
clone mapping info | 1-to-1 scattered, 1-to-many in | 1-to-many `CloneMapping` table
worm PK | generally mutant and allele, sometimes just allele | strain name
temperature type | string (e.g. "25C") | decimal
timestamps | time


Still considering these changes
- vidal plate names | e.g. 1 | e.g. vidal-1


Probably not really touching these during migration:
- attribute, node, synonym (Firoz domain)
- WellToTile (to be replaced with simple python functions)
- CherryPickList (temporary step in generating CherryPickRNAiPlate; probably meant to be deleted)
- CherryPickRNAiPlate_2011 and CherryPickRNAiPlate_lock (first ensure redundant with CherryPickRNAiPlate)
- ScoreResultsDevStaR (probably incomplete copy of RawDataWithScore that Kris made)
- PredManualScore and PredManualScoreList (what are these?)
- ReArrayRNAiPlate (first need to decide about holding onto Eliana ReArray info)


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
