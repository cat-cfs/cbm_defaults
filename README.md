# cbm_defaults

This package can be used to create a streamlined SQLite database based mainly on the parameters and table formats stored in the Archive Index Database (AIDB) of the Carbon Budget Model of the Canadian Forest Sector (CBM-CFS3). This streamlined database acts as a component in the development of next generation models based on the CBM-CFS3.

In addition, this script will also load several other [default tables](/cbm_defaults/tables) drawn from hardcoded values in the CBM-CFS3 source code.

The database schema supports localization, and it can be configured to load localized strings, such as those found in the CBM-CFS3.

## Schema

The schema can be viewed in text form [here](https://github.com/cat-cfs/cbm_defaults/blob/master/cbm_defaults/schema/cbmDefaults.ddl)


## Example application

A command line interface (CLI) app is included in this repository. The only parameter it uses is the path to a .json formatted configuration file.  The installed CLI app is named "cbm_defaults_export."

See: [main.py](cbm_defaults/scripts/main.py), [app.py](cbm_defaults/app.py)

```powershell
cbm_defaults_export --config_path ./config.json
```

The script can also be called by importing `cbm_defaults.app` where the single argument is the path to a json formatted file with configuration, or a dictionary containing the configuration.

```python
from cbm_defaults import app
app.run(config)
```

Below is an example of the configuration format.

```json
    {
        "output_path": "cbm_defaults.db",
        "default_locale": "en-CA",
        "locales": [
            {"id": 1, "code": "en-CA"},
            {"id": 2, "code": "fr-CA"}
        ],
        "archive_index_data": [
            {"locale": "en-CA",
            "path": "ArchiveIndex_Beta_Install.mdb"},
            {"locale": "fr-CA",
            "path": "ArchiveIndex_Beta_Install_fr.mdb"},
        ]
    }
```

## Migrating the database version (1.x to 2.x)

### 1.x to 2.x
The cbm_defaults.app has an update utility to migrate the version 1.x schema to 2.x. Note that changes were introduced in April 2023 for land class tracking support, and 1.x versions will not work with 2.x versions of [libcbm](https://github.com/cat-cfs/libcbm_py)

To migrate versions, enter the following script in python:

```python
from cbm_defaults.update import db_updater
db_updater.update("1x_to_2x", input_db_path, output_db_path)
```

If the cbm_defaults.app is installed to the python environment, it can be called at the command line with the following script:

```
cbm_defaults_db_update --input_db_path .\cbm_defaults.db --output_db_path  .\cbm_defaults_updated.db
```
