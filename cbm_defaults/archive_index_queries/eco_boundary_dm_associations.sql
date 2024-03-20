SELECT
    DefaultDisturbanceTypeID,
    SPUID,
    DMID
FROM tblDMAssociationDefault dma
INNER JOIN tblSPUDefault spu
    ON dma.DefaultEcoBoundaryID = spu.EcoBoundaryID
WHERE DefaultDisturbanceTypeID NOT IN (
    SELECT DISTINCT DefaultDisturbanceTypeID
    FROM tblDMAssociationSPUDefault
);
