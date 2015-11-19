# MySQL queries

Here are some queries for performing on the MySQL database directly
(i.e., not through Django query abstraction).


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


# BELOW THIS LINE NOT REFACTORED
## To find clones represented repeatedly in secondary plates

```
SELECT LibraryWell.id, intended_clone_id, COUNT(*) FROM LibraryWell
  LEFT JOIN LibraryPlate ON LibraryPlate.id = LibraryWell.plate_id
WHERE screen_stage=2
  AND intended_clone_id IS NOT NULL
  AND intended_clone_id != "L4440"
GROUP BY intended_clone_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;
```

```
SELECT A.id, B.id, A.intended_clone_id
FROM LibraryWell AS A, LibraryWell AS B,
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


## To make ENH secondary size estimates

These queries are both just a way to get a very general sense of the size of
the enhancer secondary. The number is not exact, for several reasons:

- The sum may be inflated due to overlap between the two queries (some images
  may be scored as both weak and medium, or weak and strong)
- Both queries may be inflated due library plates having more than two good
  copies
- The strong/medium query is deflated due to not counting strong/medium paired
  with unscored (it assumes two scored copies)


### Get pairwise weak enhancer counts by mutant:

```
SELECT E1.worm_strain_id, COUNT(DISTINCT E1.worm_strain_id, E1.id, S1.well, E2.id, S2.well)
FROM ManualScore AS S1, ManualScore AS S2, Experiment AS E1, Experiment AS E2
WHERE E1.library_plate_id = E2.library_plate_id
  AND E1.id < E2.id AND S1.experiment_id = E1.id AND S2.experiment_id = E2.id
  AND S1.well = S2.well
  AND E1.worm_strain_id = E2.worm_strain_id
  AND E1.is_junk = 0 AND E2.is_junk = 0
  AND (
    (S1.score_code_id=12 AND S2.score_code_id=12)
    OR (S1.score_code_id=16 AND S2.score_code_id=16)
    OR (S1.score_code_id=12 AND S2.score_code_id=16)
    OR (S1.score_code_id=16 AND S2.score_code_id=12)
  )
GROUP BY E1.worm_strain_id;
```


### Get strong or medium enhancer counts by mutant:

```
SELECT E1.worm_strain_id, COUNT(DISTINCT E1.worm_strain_id, E1.id, S1.well, E2.id, S2.well)
FROM ManualScore AS S1, ManualScore AS S2, Experiment AS E1, Experiment AS E2
WHERE E1.library_plate_id = E2.library_plate_id
  AND E1.worm_strain_id = E2.worm_strain_id
  AND E1.temperature = E2.temperature
  AND E1.is_junk = 0 AND E2.is_junk = 0
  AND E1.id < E2.id
  AND S1.experiment_id = E1.id AND S2.experiment_id = E2.id
  AND S1.well = S2.well
  AND (
    S1.score_code_id=13 OR S2.score_code_id=13
    OR S1.score_code_id=14 OR S2.score_code_id=14
    OR S1.score_code_id=17 OR S2.score_code_id=17
    OR S1.score_code_id=18 OR S2.score_code_id=18
  )
GROUP BY E1.worm_strain_id;
```
