# MySQL queries

Here are some queries for performing on the MySQL database directly
(i.e., not through Django query abstraction).


## Joining LibraryStock -> Clone -> Gene
```
SELECT Experiment.id, LibraryStock.id, Clone.id, Gene.cosmid_id, Gene.locus 
FROM Experiment
LEFT JOIN ExperimentPlate
ON Experiment.plate_id = ExperimentPlate.id
LEFT JOIN LibraryStock
ON Experiment.library_stock_id = LibraryStock.id
LEFT JOIN Clone
ON LibraryStock.intended_clone_id = Clone.id
LEFT JOIN CloneTarget
ON CloneTarget.clone_id = Clone.id
LEFT JOIN Gene
ON CloneTarget.gene_id = Gene.id
WHERE ExperimentPlate.screen_stage = 2
AND is_junk = 0;
```

## To compare Noah vs DevStaR SUP secondary scores (for Michelle)

### To generate noah.csv

```
SELECT gene, date,
  CONCAT(gene, '_', library_stock_id) AS gene_plus_library_stock,
  experiment_id, score_code_id
FROM (
  SELECT gene, date, library_stock_id, experiment_id, score_code_id
  FROM ManualScore
    LEFT JOIN Experiment ON ManualScore.experiment_id = Experiment.id
    LEFT JOIN ExperimentPlate ON Experiment.plate_id = ExperimentPlate.id
    LEFT JOIN WormStrain ON Experiment.worm_strain_id = WormStrain.id
    LEFT JOIN LibraryStock ON Experiment.library_stock_id = LibraryStock.id
  WHERE is_junk = 0  # Skip junk
    AND screen_stage = 2  # Secondary experiments only
    AND intended_clone_id IS NOT NULL  # Skip empty wells
    AND score_code_id >= 0  AND score_code_id <= 3  # Suppression scores only
    AND scorer_id = 14  # Noah scores only
  ORDER BY score_code_id DESC) x  # Choose the most optimistic if > 1 score
GROUP BY experiment_id
ORDER BY gene, date, library_stock_id, experiment_id;
```


### To generate devstar.csv

```
SELECT gene, date,
  CONCAT(gene, '_', library_stock_id) AS gene_plus_library_stock,
  experiment_id, count_adult, count_larva, count_embryo
FROM DevstarScore
  LEFT JOIN Experiment ON DevstarScore.experiment_id = Experiment.id
  LEFT JOIN ExperimentPlate ON Experiment.plate_id = ExperimentPlate.id
  LEFT JOIN WormStrain ON Experiment.worm_strain_id = WormStrain.id
  LEFT JOIN LibraryStock ON Experiment.library_stock_id = LibraryStock.id
WHERE is_junk = 0  # Skip junk
  AND screen_stage = 2  # Secondary experiments only
  AND intended_clone_id IS NOT NULL  # Skip empty wells
  AND intended_clone_id != "L4440"  # Skip L4440 controls
  AND temperature = WormStrain.restrictive_temperature  # Restrictive temp only
  AND WormStrain.id != "N2"  # Skip N2 controls
ORDER BY gene, date, library_stock_id, experiment_id;
```


## To find clones present repeatedly in secondary plates

```
SELECT LibraryStock.id, intended_clone_id, COUNT(*)
FROM LibraryStock
  LEFT JOIN LibraryPlate ON LibraryStock.plate_id = LibraryPlate.id
WHERE screen_stage=2
  AND intended_clone_id IS NOT NULL
  AND intended_clone_id != "L4440"
GROUP BY intended_clone_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;
```

```
SELECT A.id, B.id, A.intended_clone_id
FROM LibraryStock AS A, LibraryStock AS B,
  LibraryPlate AS C, LibraryPlate AS D
WHERE A.id != B.id
  AND C.id != D.id
  AND A.plate_id = C.id
  AND B.plate_id = D.id
  AND A.intended_clone_id = B.intended_clone_id
  AND A.intended_clone_id IS NOT NULL
  AND A.intended_clone_id != "L4440"
  AND B.id LIKE "universal%"
  AND C.screen_stage=2
  AND D.screen_stage=2;
```


## To estimate size of ENH secondary

These queries get a very general sense of the size of the enhancer secondary.
The numbers are inexact, for several reasons:

- The sum may be inflated due to overlap between the two queries (some images
  may be scored as both weak and medium, or weak and strong)
- Both queries may be inflated due library plates having more than two good
  copies
- The strong/medium query is deflated due to not counting strong/medium paired
  with unscored (it assumes two scored copies)


### Get pairwise weak enhancer counts by mutant

```
SELECT E1.worm_strain_id, COUNT(DISTINCT E1.worm_strain_id, E1.id, E2.id)
FROM ManualScore AS S1, ManualScore AS S2, Experiment AS E1, Experiment AS E2
WHERE E1.library_stock_id = E2.library_stock_id
  AND E1.worm_strain_id = E2.worm_strain_id
  AND E1.is_junk = 0 AND E2.is_junk = 0
  AND E1.id < E2.id
  AND S1.experiment_id = E1.id AND S2.experiment_id = E2.id
  AND ((S1.score_code_id=12 AND S2.score_code_id=12)
    OR (S1.score_code_id=16 AND S2.score_code_id=16)
    OR (S1.score_code_id=12 AND S2.score_code_id=16)
    OR (S1.score_code_id=16 AND S2.score_code_id=12)
  )
GROUP BY E1.worm_strain_id;
```


### Get strong or medium enhancer counts by mutant

```
SELECT E1.worm_strain_id, COUNT(DISTINCT E1.worm_strain_id, E1.id, E2.id)
FROM Experiment AS E1, Experiment AS E2,
  ExperimentPlate AS P1, ExperimentPlate AS P2,
  ManualScore AS S1, ManualScore AS S2
WHERE E1.plate_id = P1.id AND E2.plate_id = P2.id
  AND S1.experiment_id = E1.id AND S2.experiment_id = E2.id
  AND P1.temperature = P2.temperature
  AND E1.library_stock_id = E2.library_stock_id
  AND E1.worm_strain_id = E2.worm_strain_id
  AND E1.is_junk = 0 AND E2.is_junk = 0
  AND E1.id < E2.id
  AND (S1.score_code_id=13 OR S2.score_code_id=13
    OR S1.score_code_id=14 OR S2.score_code_id=14
    OR S1.score_code_id=17 OR S2.score_code_id=17
    OR S1.score_code_id=18 OR S2.score_code_id=18
  )
GROUP BY E1.worm_strain_id;
```
