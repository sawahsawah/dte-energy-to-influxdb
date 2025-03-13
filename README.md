# DTE Energy Usage Script

This script fetches hourly energy usage data from DTE Energy's XML API, processes the data, and writes it to an InfluxDB instance for analysis.

## Features
- Fetches electric usage data from DTE's XML API.
- Parses and converts the data into a structured format.
- Adjusts timestamps for correct time zone handling.
- Sends the processed data to InfluxDB for visualization and analysis.

## Requirements
- Python 3.x
- `requests` library
- `xml.etree.ElementTree` for XML parsing
- `InfluxDBClient` from the InfluxDB Python client

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/sawahsawah/dte-energy-to-influxdb.git
   cd dte-energy-to-influxdb
   ```
2. Install dependencies:
   ```sh
   pip install requests influxdb-client
   ```
3. Configure your environment variables or modify the script with:
   - `DATA_URL` (URL for DTE's XML data)
   - `INFLUXDB_URL` (InfluxDB server address)
   - `INFLUXDB_TOKEN` (InfluxDB authentication token)
   - `INFLUXDB_ORG` (InfluxDB organization)
   - `INFLUXDB_BUCKET` (InfluxDB bucket name)

## Usage
Run the script manually with:
```sh
python dte-energy-to-influxdb.py
```
