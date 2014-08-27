    SELECT D1.mutant, D1.temperature, node_primary_name, clone, S1.score,
        S2.score, D1.expID, S1.ImgName, D2.expID, S2.ImgName
    FROM ManualScore AS S1, ManualScore AS S2, RawData AS D1, RawData AS D2, RNAiPlate AS P
    WHERE D1.RNAiPlateID=D2.RNAiPlateID AND D1.RNAiPlateID=P.RNAiPlateID
    AND D1.expID<D2.expID AND S1.expID=D1.expID AND S2.expID=D2.expID
    AND S1.ImgName=S2.ImgName AND S1.ImgName=P.ImgName
    AND D1.mutant=D2.mutant AND D1.temperature=D2.temperature
    AND D1.isJunk=0 and D2.isJunk=0
    AND ((D1.mutant="mbk-2" AND D1.temperature="22.5C")
        OR (D1.mutant="par-2" AND D1.temperature="20C")
        OR (D1.mutant="zen-4" AND D1.temperature="15C"))
    AND ((S1.score=12 AND S2.score=12) OR (S1.score=16 AND S2.score=16)
        OR (S1.score=12 AND S2.score=16) OR (S1.score=16 AND S2.score=12))
    ORDER BY mutant, node_primary_name;
