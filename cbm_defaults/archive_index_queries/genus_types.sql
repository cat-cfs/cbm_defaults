SELECT tblGenusTypeDefault.GenusID,
tblGenusTypeDefault.GenusName
FROM tblGenusTypeDefault
GROUP BY tblGenusTypeDefault.GenusID,
tblGenusTypeDefault.GenusName;