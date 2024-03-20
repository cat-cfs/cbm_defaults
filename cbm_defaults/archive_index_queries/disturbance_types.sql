SELECT DistTypeID, DistTypeName, Description
FROM tbldisturbancetypedefault
WHERE disttypeid IN (
    SELECT DISTINCT defaultdisturbancetypeid
    FROM tbldmassociationdefault
) OR disttypeid IN (
    SELECT DISTINCT defaultdisturbancetypeid
    FROM tbldmassociationspudefault
)