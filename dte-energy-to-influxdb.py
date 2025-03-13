"""This script pulls your electric energy usage from your personal DTE usage webpage. It then converts it into the proper timeseries format and uploads the data to InfluxDB."""
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import pytz

# Define timezone
LOCAL_TZ = pytz.timezone("YOUR-TIMEZONE") 

# InfluxDB configuration
INFLUXDB_URL = "YOUR-INFLUXDB-URL"
INFLUXDB_TOKEN = "YOUR-INFLUXDB-TOKEN"
INFLUXDB_ORG = "ORG-NAME"
INFLUXDB_BUCKET = "BUCKET-NAME"

# URL to fetch the XML data
DATA_URL = "YOUR-DTE-USAGE-DATA-URL"

def fetch_data(url):
    """Fetch the XML data from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_electric_data(xml_data):
    """Parse the XML data for electric readings and adjust timestamps to UTC."""
    root = ET.fromstring(xml_data)
    readings = []

    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title")
        if title is not None and title.text == "Electric readings":
            for interval_block in entry.findall("{http://www.w3.org/2005/Atom}content/{http://naesb.org/espi}IntervalBlock"):
                for reading in interval_block.findall("{http://naesb.org/espi}IntervalReading"):
                    time_period = reading.find("{http://naesb.org/espi}timePeriod")
                    reading_start = int(time_period.find("{http://naesb.org/espi}start").text)
                    reading_duration = int(time_period.find("{http://naesb.org/espi}duration").text)
                    value = float(reading.find("{http://naesb.org/espi}value").text)

                    # Convert value to kWh
                    converted_value = value / 1000

                    # Convert timestamp to UTC if it is in local time
                    dt_local = datetime.fromtimestamp(reading_start, LOCAL_TZ)  # Convert from Unix timestamp to local datetime
                    dt_utc = dt_local.astimezone(pytz.utc)  # Convert to UTC
                    reading_start_utc = int(dt_utc.timestamp())  # Convert back to Unix time

                    readings.append({
                        "timestamp": reading_start_utc,  # Store UTC timestamps
                        "duration": reading_duration,
                        "value_kwh": converted_value,
                        "type": "electric"
                    })

    return readings

def write_to_influx(readings):
    """Write the parsed readings to InfluxDB."""
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)

        for reading in readings:
            point = (
                Point("energy_usage")
                .tag("type", reading["type"])
                .field("value_kwh", reading["value_kwh"])
                .time(reading["timestamp"], WritePrecision.S)
            )
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        client.close()
        print("Data successfully written to InfluxDB.")
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")

def main():
    try:
        # Fetch the XML data
        xml_data = fetch_data(DATA_URL)

        # Parse the electric data
        readings = parse_electric_data(xml_data)
        
        # Sort readings by timestamp and get the 24 most recent
        sorted_readings = sorted(readings, key=lambda x: x['timestamp'], reverse=True) #to limit, [:1000]

        # Print sorted readings
        #print(sorted_readings)

        # Send data to InfluxDB
        write_to_influx(sorted_readings)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()