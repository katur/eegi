Notes about how to migrate the data from the GenomeWideGI MySQL database into
the eegi MySQL database for this Django project.


Database migration can be achieved with `./manage.py migrate_legacy_data`,
which optionally accepts a subset of steps to perform
(see its docs for details).


The script is slow, due to creating a Python object for each row
(this object is validated, and then added to the database if it does not exit,
or used to update the database if it does exist and has changed).


SQL queries could instead be performed to avoid this per-row validation.
If you would like to do that, please see below.


WormStrain (did not exist in GenomeWideGI)
------------------------------------------
Since it is less than 30 rows, I simply populated by hand,
referencing the Google Doc "GWGI worm strains and temperatures".


LibraryPlate (did not exist in GenomeWideGI)
--------------------------------------------
Add 384 plates and Eliana Rearray plates by hand.

Then:

  INSERT INTO LibraryPlate (id, screen_stage, number_of_wells)
  SELECT DISTINCT RNAiPlateID, 1, 96 FROM RNAiPlate;

  INSERT INTO LibraryPlate (id, screen_stage, number_of_wells)
  SELECT DISTINCT RNAiPlateID, 2, 96 FROM CherryPickRNAiPlate;


Experiment (formerly RawData)
-----------------------------
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


ManualScoreCode (formerly ManualScoreCode)
------------------------------------------


ManualScore (formerly ManualScore)
----------------------------------


DevstarScore (formerly RawDataWithScore)
----------------------------------------


