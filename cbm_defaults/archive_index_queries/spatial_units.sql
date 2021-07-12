SELECT 
tblSPUDefault.SPUID,
tblSPUDefault.EcoBoundaryID,
tblSPUDefault.AdminBoundaryID,
tblEcoBoundaryDefault.AverageAge
FROM tblEcoBoundaryDefault INNER JOIN
tblSPUDefault ON tblEcoBoundaryDefault.EcoBoundaryID =
    tblSPUDefault.EcoBoundaryID;
