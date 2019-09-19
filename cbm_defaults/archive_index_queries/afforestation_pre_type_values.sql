SELECT tblSPUDefault.SPUID,
tblSVLAttributesDefaultAfforestation.PreTypeID,
tblSVLAttributesDefaultAfforestation.SSoilPoolC_BG
FROM tblSVLAttributesDefaultAfforestation INNER JOIN
tblSPUDefault ON (
	tblSVLAttributesDefaultAfforestation.EcoBoundaryID =
		tblSPUDefault.EcoBoundaryID
	) AND (
		tblSVLAttributesDefaultAfforestation.AdminBoundaryID =
			tblSPUDefault.AdminBoundaryID)
GROUP BY tblSPUDefault.SPUID,
tblSVLAttributesDefaultAfforestation.PreTypeID,
tblSVLAttributesDefaultAfforestation.SSoilPoolC_BG;