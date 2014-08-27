Notes about how to migrate the data from the GenomeWideGI MySQL database into
the eegi MySQL database for this Django project.


eegi.WormStrain
---------------
This table did not exist in GenomeWideGI.

Since it is less than 30 rows, I simply populated by hand,
referencing the Google Doc "GWGI worm strains and temperatures".


eegi.ClonePlate
---------------
This table also did not exist in GenomeWideGI.

There are very few 384-well plates, so I added these by hand.

Insert Primary 96-well plates:
> SELECT DISTINCT RNAiPlateID FROM RNAiPlate;

Insert Secondary 96-well plates:
> SELECT DISTINCT RNAiPlateID FROM CherryPickRNAiPlate;


eegi.Experiment
---------------
First, copy GenomeWideGI.RawData to eegi.RawData.

Correct misspelled allele in eegi.RawData:
> UPDATE RawData SET mutantAllele='zu310' WHERE mutantAllele='zc310';

Temporarily set eegi.WormStrain.gene to 'N2' for N2, in order for join to work
(the old database had N2 listed as a mutation).

Then:
> INSERT INTO experiments.experiment
> SELECT expID, worms.name, plates.name,
>   CAST(SUBSTRING_INDEX(temperature, 'C', 1) AS DECIMAL(3,1)),
>   CAST(recordDate AS DATE), ABS(isJunk), comment
> FROM RawData
> LEFT JOIN wormstrains_wormstrain AS worms
> ON RawData.mutant=worms.gene
> AND RawData.mutantAllele=worms.allele
> LEFT JOIN clones_cloneplate AS plates
> ON RawData.RNAiPlateID=plates.name
> WHERE (expID < 40000 OR expID > 49999)
> AND RNAiPlateID NOT LIKE "Julie%";
