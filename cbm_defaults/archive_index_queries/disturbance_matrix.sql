SELECT
tblDMValuesLookup.DMID,
tblDMValuesLookup.DMRow,
tblDMValuesLookup.DMColumn,
tblDMValuesLookup.Proportion
FROM tblDMValuesLookup
WHERE tblDMValuesLookup.DMID=?;
