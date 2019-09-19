SELECT tblForestTypeDefault.ForestTypeID,
tblGrowthMultiplierDefault.AnnualOrder,
tblGrowthMultiplierDefault.GrowthMultiplier
FROM (
	tblDisturbanceTypeDefault INNER JOIN
		tblGrowthMultiplierDefault ON
		tblDisturbanceTypeDefault.DistTypeID =
		tblGrowthMultiplierDefault.DefaultDisturbanceTypeID
	) INNER JOIN tblForestTypeDefault ON
		IIF(
			tblGrowthMultiplierDefault.DefaultSpeciesTypeID = 1,
			tblGrowthMultiplierDefault.DefaultSpeciesTypeID,
			tblGrowthMultiplierDefault.DefaultSpeciesTypeID + 1
		) = tblForestTypeDefault.ForestTypeID
GROUP BY tblDisturbanceTypeDefault.DistTypeID,
tblForestTypeDefault.ForestTypeID,
tblGrowthMultiplierDefault.AnnualOrder,
tblGrowthMultiplierDefault.GrowthMultiplier
HAVING (((tblDisturbanceTypeDefault.DistTypeID)=?));