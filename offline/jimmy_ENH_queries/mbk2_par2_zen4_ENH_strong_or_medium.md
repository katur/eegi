    SELECT mutant, temperature, node_primary_name, clone, score,
        MS.expID, MS.ImgName
    FROM ManualScore AS MS, RawData AS RD, RNAiPlate AS RP
    WHERE RD.expID=MS.expID AND RD.RNAiPlateID=RP.RNAiPlateID
    AND MS.ImgName=RP.ImgName
    AND isJunk=0
    AND ((mutant="mbk-2" AND temperature="22.5C")
        OR (mutant="par-2" AND temperature="20C")
        OR (mutant="zen-4" AND temperature="15C"))
    AND (score="13" OR score="14" OR score="17" OR score="18")
    ORDER BY mutant, node_primary_name;
