from cbmdefaultsinterface import CBMDefaultsInterface
from accessdb import AccessDB
from cbmdefaultsbuilder import CBMDefaultsBuilder

archiveIndexPath = r"C:\Program Files (x86)\Operational-Scale CBM-CFS3\Admin\DBs\ArchiveIndex_Beta_Install.mdb"
cbmDefaultsPath = r"\\dstore\carbon1\CBM Tools and Development\CBM3.5\documentation\next_generation_schema\populateCBMDefaults\cbm_defaults.db"
ddlPath = r"\\dstore\carbon1\CBM Tools and Development\CBM3.5\documentation\next_generation_schema\populateCBMDefaults\cbmDefaults.ddl"

cbmDefaults = CBMDefaultsInterface(cbmDefaultsPath)
cbmDefaults.executeDDLFile(ddlPath)
aidb = AccessDB(archiveIndexPath)
builder = CBMDefaultsBuilder(aidb, cbmDefaults)
builder.run()
cbmDefaults.commitChanges()




