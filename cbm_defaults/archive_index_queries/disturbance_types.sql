SELECT tblDisturbanceTypeDefault.DistTypeID,
tblDisturbanceTypeDefault.DistTypeName,
tblDisturbanceTypeDefault.Description
FROM tblDisturbanceTypeDefault LEFT JOIN (
	SELECT tblDMAssociationDefault.DefaultDisturbanceTypeID
	FROM tblDMAssociationDefault
	GROUP BY tblDMAssociationDefault.DefaultDisturbanceTypeID) as dma
	on tblDisturbanceTypeDefault.DistTypeID =
	dma.DefaultDisturbanceTypeID
WHERE dma.DefaultDisturbanceTypeID is not Null;
