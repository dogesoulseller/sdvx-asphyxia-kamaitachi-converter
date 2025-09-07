# SDVX Asphyxia to Kamaitachi Converter

A Python script to import Sound Voltex scores from an Asphyxia database and format them for use with the Kamaitachi batch importer.

## Overview

This tool extracts Sound Voltex score data from an Asphyxia database file and converts it into a
JSON format compatible with the Kamaitachi score tracker's batch importer.

https://kamai.tachi.ac

Meant for use with the plugin at https://github.com/22vv0/asphyxia_plugins

## Setup

1. Place your Asphyxia database file next to the script (preferably as `sdvx@asphyxia.db`, taken from the `asphyxia/savedata` folder)

2. Configure the script by editing `main.py`:
   - Set your `ASPHYXIA_PROFILE_ID` for score filtering (get it from the Asphyxia Web UI)
   - Adjust `PRESERVE_FAILS` as needed

## Usage

Run the script:
```bash
    python main.py
```

The script will generate an output JSON file that should be provided to https://kamai.tachi.ac/import/batch-manual

## Requirements

- Python 3.10+