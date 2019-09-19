        SELECT tblSPUDefault.SPUID, tblSPUDefault.AdminBoundaryID,
        tblSPUDefault.EcoBoundaryID, tblClimateDefault.MeanAnnualTemp,
        tblEcoBoundaryDefault.AverageAge
        FROM (
            tblSPUDefault INNER JOIN tblClimateDefault ON
                tblSPUDefault.SPUID = tblClimateDefault.DefaultSPUID
            ) INNER JOIN tblEcoBoundaryDefault ON
            tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID
        WHERE tblClimateDefault.Year=1981;
