import os 
from cbmdefaultsinterface import CBMDefaultsInterface
from accessdb import AccessDB
from cbmdefaultsbuilder import CBMDefaultsBuilder
from loghelper import *

start_logging("populate_cbm_defaults.log")

aidb_dir = r"M:\CBM Tools and Development\Builds\OpScaleArchiveIndex\20180828"

aidb_paths = {
    "en-CA": os.path.join(aidb_dir, "ArchiveIndex_Beta_Install.mdb"),
    "fr-CA": os.path.join(aidb_dir, "ArchiveIndex_Beta_Install_fr.mdb"),
    "es-MX": os.path.join(aidb_dir, "ArchiveIndex_Beta_Install_es.mdb"),
    "ru-RU": os.path.join(aidb_dir, "ArchiveIndex_Beta_Install_ru.mdb"),
    "pl-PL": os.path.join(aidb_dir, "ArchiveIndex_Beta_Install.mdb")#since there is no polish aidb, use the english terms
}

cbmDefaultsPath = r"C:\dev\cbm_defaults\cbm_defaults.db"
ddlPath = "cbmDefaults.ddl"

cbmDefaults = CBMDefaultsInterface(cbmDefaultsPath)
cbmDefaults.executeDDLFile(ddlPath)

builder = CBMDefaultsBuilder(aidb_paths, cbmDefaults)
builder.run()
cbmDefaults.commitChanges()

