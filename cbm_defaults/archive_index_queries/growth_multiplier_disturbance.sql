SELECT tblGrowthMultiplierDefault.DefaultDisturbanceTypeID
FROM tblGrowthMultiplierDefault
WHERE (((tblGrowthMultiplierDefault.GrowthMultiplier)<1))
GROUP BY tblGrowthMultiplierDefault.DefaultDisturbanceTypeID;
