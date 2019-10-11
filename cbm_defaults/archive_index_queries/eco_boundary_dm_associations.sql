SELECT
    tblDMAssociationDefault.DefaultDisturbanceTypeID,
    tblSPUDefault.SPUID,
    tblDMAssociationDefault.DMID
FROM
    tblDMAssociationDefault
INNER JOIN tblSPUDefault ON
    tblDMAssociationDefault.DefaultEcoBoundaryID = tblSPUDefault.EcoBoundaryID
GROUP BY
    tblDMAssociationDefault.DefaultDisturbanceTypeID,
    tblSPUDefault.SPUID,
    tblDMAssociationDefault.DMID,
    tblDMAssociationDefault.DefaultDisturbanceTypeID
HAVING
    tblDMAssociationDefault.DefaultDisturbanceTypeID<>1;
