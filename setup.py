import os
from setuptools import setup
from setuptools import find_packages


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="cbm_defaults",
    version="2.0.0",
    description="CBM-CFS3 archive-index database to sqlite utility",
    keywords=["cbm-cfs3"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Carbon Accounting Team - Canadian Forest Service",
    author_email="scott.morken@canada.ca",
    maintainer="Scott Morken",
    maintainer_email="scott.morken@canada.ca",
    license="MPL-2.0",
    url="",
    download_url="",
    packages=find_packages(exclude=["test*"]),
    package_data={
        "cbm_defaults": [
            "schema/cbmDefaults.ddl",
            "tables/*.csv",
            "archive_index_queries/*.sql",
        ]
    },
    entry_points={
        "console_scripts": [
            "cbm_defaults_export = cbm_defaults.scripts.main:main"
        ]
    },
    install_requires=requirements,
)
