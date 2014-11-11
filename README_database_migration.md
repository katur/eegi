# Database Migration Notes

These notes are about migrating the genome-wide GI project data
from the legacy MySQL database (primarily pleiades.GenomeWideGI, plus
Noah's SUP Secondary scores from pleiades.GWGI2.ScoreResultsManual)
to the redesigned MySQL database (eegi).

-----------------------------------------------------------------------------------

## Main Database Migration Script

A script is used to migrate new or updated records.
It does not yet account for deleted records,
so should be run from scratch on a truncated database
just prior to the official migration to the new database.

The script lives in `utils/management/commands`, and can be run with:

    ./manage.py migrate_legacy_database

Please see the script's documentation for more information
(including where to enter legacy database connection information,
optional arguments to run only part of the script,
the actual queries performed on the legacy database, etc).

In a nutshell, however, the script is broken into about 10 steps,
each step roughly corresponding to migrating a single table.
These steps are ordered based on dependencies between steps.
Within each step, the legacy database is queried
(e.g. to fetch all the records from some legacy table).
For each record in the query result,
various validation and conversion steps are used to create a Python object
that is compatible with a record in the new database.
Finally, if a corresponding record does not exist in the new database,
the object is saved to the new database;
otherwise, the corresponding object is updated to reflect changes
that have occured since the last migration.

This process of creating a Python object for every single record
(~4 million records) is very slow. But it only needs to be run
a few times during development of the new database, and then once
just prior to the official migration to the new database.
For this reason, the easy validation it offers was favored over a faster
approach (such as clearing the new database, copying the old tables into the
new database, performing various conversions on the old tables with SQL,
inserting the old rows into the new tables with SQL, and deleting the old
tables).

-----------------------------------------------------------------------------------

## Migrating Empty LibraryWells

After using the main script to migrate the LibraryWell table, 
another script is used to add rows to representing 'empty' wells in the database:

    ./manage.py add_empty_LibraryWells

This is separate from the main script because empty wells were not represented
in the previous database's library tables.

After running this script, you should re-run the LibraryWell step of the main
script, to resolve empty well parents of rearrayed plates. The legacy 
database did not represent "empty wells" in its library 
tables, but it did not enforce foreign key constraints, and therefore allowed
some "impossible" parent relationships between LibraryWells (parent wells that 
themselves did not have rows in the database). The main script ignores these 
impossiblilities (by leaving parent null), because the new database does 
enforce FK constraints. However, a handful of these are resolved once
the empty library wells are accounted for.

In addition, the legacy database did not include sequencing results from supposedly
empty wells. So for the sequencing plates whose parent wells are resolved
using the legacy database (plates 1-56), the source of empty wells must be resolved
after this point.

-----------------------------------------------------------------------------------

## Migrating Sequencing Data

A third script is used to migrate sequencing data. The reason this script is 
separate is that it uses a very different approach than the other database migration 
steps (since the legacy database did not store raw sequencing data, nor is it up to date).

To migrate the sequencing data, first copy all the genewiz sequencing output to your
local machine:

    scp username@machine:~genewiz/GenomeWideGI/ destination

Note that this genewiz directory includes ALL sequencing done by the lab;
not just for the GI project.

Run Hueyling's script to remove the date from the Seq and AB1 directories
(this script is located in the directory just copied):

    cd destination
    perl rmDateFromSeqAB1.pl

There is no need to run her other scripts; the new script it written to work with .csv or .xls.

Second, copy the GI team Google Doc `tracking_numbers` to your machine, which includes
genewiz tracking numbers for all GI-specific sequencing plates.

Now run the script to migrate the data (see the script for database connection
requirements):

    ./manage.py migrate_sequencing_data tracking_numbers genewiz_output_root

-----------------------------------------------------------------------------------

## Reference of Changes


### General
concept | GenomeWideGI | eegi
------- | ------------ | ----
database name | GenomeWideGI | eegi (a la Python package name)
table names | usually CamelCase, but not always | always CamelCase (a la Python class names)
field names | mishmash of under_scores, mixedCase, CamelCase | always underscores (a la Python variables)
"well" versus "tile" | some tables have one, some the other, some both | use only "well" throughout the database, with accessible Python functions to convert
well names | typically "A01" style, but "A1" for Vidal plates | consistently 3 characters long (except special case of within Orfeome clone *name*; see `clones` decisions below)



### `worms` app
concept | GenomeWideGI | eegi
------- | ------------ | ----
information about worm strains | no table | `WormStrain` table
referring to worm strains | generally mutant and allele, sometimes just allele | FK to `WormStrain`
par-1 allele | zc310 | zu310



### `clones` app
concept | GenomeWideGI | eegi
------- | ------------ | ----
clone names | sjj\_X and mv\_X | sjj\_X and GHR-X\@X. Note: The well within Orfeome clone names is "A1"-style for GHR-10%, but "A01"-style for GHR-11% onward. I'm leaving this as is for consistency with the Orfeome database. But in the fields of `LibraryWell` that refer to the location of these cloens (i.e. `LibraryWell.id` and `LibraryWell.well`), I'll consistently use "A01" style.
clone mapping info | 1-to-1, scattered over many tables (wherever `clone` is accompanied by `node_primary_name` and/or `gene`) | All mapping isolated to `clones` app, which is connected to rest of database only by FK to `RNAiClone`. Mapping will be 1-to-many.

**Still to do**
- Decide on schema for Firoz's tables re: mapping!
- Confirm Kris and Firoz are okay ditching the "RNAi" prefix for clone tables. If so, rename RNAiClone in the project.



### `library` app: plate-level
concept | GenomeWideGI | eegi
------- | ------------ | ----
plate-level information about library plates | no table | `LibraryPlate` table
vidal plate names | integers 1-21 | prefix with "vidal", e.g., "vidal-4"
plate names in general | mishmash of hyphens (e.g. I-2-B1 and GHR-10010) and underscores (e.g. b1023\_F5 and Eliana\_Rearray\_2) | hyphens only (for more readable `LibraryWell.id`, e.g., b1023-F5\_F05)

**Still to do**
- Delete `LibraryPlate.screen_stage` since it's redundant with `Experiment.screen_level`. Or, if we think it would be useful to keep it, rename to `LibraryPlate.screen_level` for consistency.
- Add the prefix to vidal plate names, and convert the plate name underscores to hyphens.



### `library` app: well-level
concept | GenomeWideGI | eegi
------- | ------------ | ----
well-level clone identities of library plates | `RNAiPlate` (primary plates), `CherryPickRNAiPlate` (secondary) and `ReArrayRNAiPlate` (Julie and Eliana rearrays) | Combine all plates in `LibraryWell`. Do not migrate Julie plates.
well-level parent relationships from primary plates to source plates (i.e., to Ahringer 384 plate or GHR-style Orfeome plates) | can be derived from `RNAiPlate` columns `chromosome`, `384PlateID`, and `384Well` (though confusing because 384PlateID is incomplete without chromosome for Ahringer 384 plates, and because the Orfeome plates are actually 96 wells) | capture with FK from `LibraryWell` to `LibraryWell`
well-level parent relationships from secondary plates to primary plates | `CherryPickTemplate` (but incomplete; many rows missing) | capture with FK from `LibraryWell` to `LibraryWell`
PK for `LibraryWell` | two fields: plate and well | single field, in format plate\_well (e.g., I-1-A1\_H05)
Wells with no clone (theoretically) | not included in database | include in database. Due to mistakes in the bacterial library, some wells with no intended clone do grow, and sometimes even have phenotypes. We photograph these wells, and sometimes even score and sequence them. So we should represent them in the database, with `intended_clone_id` null.

**Still to do**
- There are a handful (about ten) ambiguities regarding the source of secondary plate wells, due to the legacy database storing these as ambiguous mv_cosmid only, and `CherryPickTemplate` being out of date. Since these are easy to fix manually, make sure to do this just prior to the official migration.



### `library` app: sequencing
concept | GenomeWideGI | eegi
------- | ------------ | ----
sequencing results | `SeqPlate` table, which stores mostly conclusions (missing most Genewiz output) | `LibrarySequencing`, which stores mostly Genewiz output
recent sequencing results (plates 56-70) | not present in database | include in new database by referencing our google docs
Genewiz resequencing of same well | forced into one row of `SeqPlate` | allow many-to-one sequences-per-well. Example: genewiz tracking 10-190633217, tube 90, has two separate sequencing (Tube Label JL90 and JL90\_R, with separate seq and ab1 files). However, HL put these on the same row, only indicated by multiple values for SeqResult (e.g. BN/BN) and seqClone (sjj\_F57A10.2|789|sjj_T24A6.1|857). I am putting these in separate rows.
Genewiz output corresponding to no known clone (due to supposedly empty wells in the sequencing plates) | skipped in database | include in database (so it is clear what these sequences / ab1 files are from)

**Still to do**
- After adding empty LibraryWells to the database, fill in the corresponding parent relationships for sequencing wells.
- After accounting for empty wells, migrate plates 57-70 using the Google Docs.
- Add Firoz's resulting clones, once calculated (note that I am not migrating either Hueyling's quality categorization, e.g. BY/GN, or her resulting clone).



### `experiments` app: experiments
concept | GenomeWideGI | eegi
------- | ------------ | ----
experiments table | `RawData` | `Experiment`
temperature datatype | string (e.g. "25C") | decimal
experiment date datatype | string | date
is\_junk datatype | integer | boolean
is\_junk values | -1 "definite junk", never to be trusted (e.g. wrong worms, wrong bacteria); 1 "possible junk", not up to standards (e.g. temperature slightly off, too many worms per well, bacterial contamination). However, these definitions weren't used consistently. | No separation of possible vs definite junk. Anything untrustworthy should either be deleted (including pictures), or have a comment in the database explaining why it is junk, in order to discourage future consideration (all "definite junk" to date has such a comment, so it is okay to migrate these experiments as generic junk).



### `experiments` app: manual scores
concept | GenomeWideGI | eegi
------- | ------------ | ----
manual scores table(s) | `ManualScore` (primary) and `ScoreResultsManual` (secondary) | one table: `ManualScore`
score time datatype | originally int year, string month, int day, string time; scoreYMD eventually added, but incomplete (since not updated by most of HL's programs to add experiments), and doesn't include timestamp | timezone-aware datetime
scorer | string of username | FK to `User`
score category -8: secondary pool | was used temporarily to flag 'uncertain' scores. now has no corresponding scores. | do not migrate this category or scores
score category -1: not sure | only Julie scores have this value | do not migrate this category or scores
score category 4: No Larvae | K/S mel-26 scores, for some DevStaR test | do not migrate this category or scores
score category 5: Larvae Present | K/S mel-26 scores, for some DevStaR test | do not migrate this category or scores
score category 6: A lot of Larvae | K/S mel-26 scores, for some DevStaR test (on re-examination, no obvious suppressors, since the L4440 control this week had tons of larvae) | do not migrate this category or scores
score category -6: Poor Image Quality | very old scores only | convert to -7
score category -5: IA Error (i.e., DevStaR issues that aren't caused by poor image quality) | very old scores only | migrate, but omit from interface for now (possible delete later for simplicity)
scorer expPeople | only one score ("no bacteria") | convert to hueyling
scorer Julie (MySQL default for scoredBy) | All her scores have an improper date, and were probably not added via the traditional scoring interface. All scores are either spn-4 scores from junk experiments (perhaps Julie gave Hueyling at Excel sheet of scores, which might be why Hueyling made "Julie" the default scoredBy), or "no bacteria" scores (which we believe Hueyling and Amelia entered, perhaps using Katherine's growth history data) | convert "no bacteria" scores to hueyling; do not migrate spn-4 scores (these experiments are useless, due to using a reverting spn-4 line)
scorer alejandro | only ENH scores | do not migrate any alejandro scores (not well trained, and did not score much)
scorer katy | only pre-consensus div-1 ENH scores | do not migrate any katy scores (scored before ENH criteria finalized)
scorer lara | some pre-consensus ENH scores | do not migrate lara's ENH scores (scored before ENH criteria finalized)
scorer eliana | some pre-consensus ENH scores | do not migrate eliana's ENH scores (scored before ENH criteria finalized)
scorer kelly | some pre-consensus ENH scores | probably do not migrate kelly's ENH scores (scored before ENH criteria finalized, plus some training issues), but try to confirm that they were not used in amelia's cutoff analysis
scorers sherly, giselle | some pre-consensus ENH scores | pending decision about whether to migrate their ENH scores. The danger in keeping these is that they are inconsistent with our eventual scoring criteria (and they are redundant, since everything was eventually scored by the "official" scorers noah, koji, and mirza). But we need to investigate 1) were these scores used in amelia's cutoff analysis? and 2) were all Mediums and Strongs captured by the official scorers?



### `experiments` app: DevStaR scores
concept | GenomeWideGI | eegi
------- | ------------ | ----
DevStaR scores table | `RawDataWithScore` | `DevstarScore`
worm stage names | mishmash of plural and singular, and worm/adult | consistently using singular adult, larva, embryo
datatype for embryo per adult, larva per adult | INTEGER | FLOAT
datatype for survival/lethality | truncated to 6 digits past decimal | more precision
survival and lethality, if no adults | 0 | calculate the regular way, using embryo and larva numbers
embryo per adult and larva per adult, if no adults | 0 | null

**Still to do**
- Per HL, I kept the embryo count as an integer. Should we change it to a float?



### Tables not touched during migration
- attribute, node, synonym (Firoz/mapping domain; he can take info from them if he wants)
- CherryPickList (temporary step in generating CherryPickRNAiPlate; probably meant for deletion)
- CherryPickRNAiPlate\_2011 and CherryPickRNAiPlate\_lock (I should ensure they are redundant with CherryPickRNAiPlate)
- ScoreResultsDevStaR (but ensure it is just an incomplete copy of RawDataWithScore, made by Kris)
- PredManualScore and PredManualScoreList (but figure out why these exist!)
- WellToTile (to be replaced with simple Python functions)



<!--
-----------------------------------------------------------------------------------
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
