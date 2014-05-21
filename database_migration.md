Notes about how to migrate the data from the GenomeWideGI MySQL database into
the eegi MySQL database for this Django project.

eegi.WormStrain
---------------
This table did not exist in GenomeWideGI.
Simply populat by hand referencing the Google Doc (few total rows).

eegi.ClonePlate
---------------
This table also did not exist in GenomeWideGI.
Add the 384-well plates by hand (very few).
Insert Primary and Secondary 96-well plates by querying distinct RNAiPlateID
from RNAiPlate and CherryPickRNAiPlate (respectively).

eegi.Experiment
---------------
First, copy GenomeWideGI.RawData to eegi.RawData (temporarily).

Correct a misspelled allele in eegi.RawData:
  UPDATE RawData SET mutantAllele='zu310' WHERE mutantAllele='zc310';

Temporarily set eegi.WormStrain.gene to 'N2' for N2, in order for join to work

Select the fields needed for eegi.Experiment:
  INSERT INTO experiments.experiment
  SELECT expID, worms.name, plates.name,
    CAST(SUBSTRING_INDEX(temperature, 'C', 1) AS DECIMAL(3,1)),
    CAST(recordDate AS DATE), ABS(isJunk), comment
  FROM RawData
  LEFT JOIN wormstrains_wormstrain AS worms
  ON RawData.mutant=worms.gene
  AND RawData.mutantAllele=worms.allele
  LEFT JOIN clones_cloneplate AS plates
  ON RawData.RNAiPlateID=plates.name
  WHERE (expID < 40000 OR expID > 49999)
  AND RNAiPlateID NOT LIKE "Julie%";
