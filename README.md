

```
# Sentinel Acquisition Overlap Tool

A Python tool to find temporal and spatial overlaps between Sentinel-1 and Sentinel-2 satellite acquisitions for any location on Earth.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Features

- **Temporal Overlap Detection**: Find acquisitions within user-defined time windows
- **Spatial Overlap Calculation**: Percentage-based overlap of acquisition footprints
- **Cloud Cover Filtering**: Automatically exclude cloudy Sentinel-2 images
- **Flexible Search Parameters**: Adjustable search area and time thresholds
- **Sentinel Hub Integration**: Direct access to Copernicus data catalog

## Installation

1. **Clone Repository**
```
git clone https://github.com/getnetdemil/sentinel-satellite-overlapping.git
cd sentinel-overlap-tool
```

2. **Install Dependencies**
```
pip install -r requirements.txt
```

3. **Configure Sentinel Hub Credentials**
   - Create `.env` file:
   ```
   SH_CLIENT_ID="your-client-id"
   SH_CLIENT_SECRET="your-client-secret"
   ```
   - Register at [Sentinel Hub](https://www.sentinel-hub.com/) if you don't have credentials

## Usage

Basic command:
```
python sentinel_overlap.py <latitude> <longitude> <start_date> <end_date>
```

### Example: New York City
```
python sentinel_overlap.py 40.7128 -74.0060 01:11:23 07:11:23 \
  --buffer 0.5 --max-diff 180 --min-overlap 10
```

### Parameters
| Parameter       | Description                                  | Default  |
|-----------------|----------------------------------------------|----------|
| `latitude`      | Target latitude in decimal degrees           | Required |
| `longitude`     | Target longitude in decimal degrees          | Required |
| `start_date`    | Start date in DD:MM:YY format                | Required |
| `end_date`      | End date in DD:MM:YY format                  | Required |
| `--buffer`      | Search radius in degrees (1° ≈ 111km)        | 0.5      |
| `--max-diff`    | Maximum time difference in minutes           | 180      |
| `--min-overlap` | Minimum spatial overlap percentage required  | 1.0      |

## Sample Output
```
Found 3 overlapping acquisitions between 01-Nov-2023 and 07-Nov-2023
Location: 40.7128°N, -74.0060°E
Max time difference: 180 mins | Min overlap: 10.0%

Overlap 1:
  Sentinel-1: 2023-11-03 09:30 UTC
  Sentinel-2: 2023-11-03 10:15 UTC
  Δ Time: 45.0 minutes
  Overlap Percentage: 78.32%
  Cloud Cover: 12.5%
```

## License
MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments
- Satellite data provided by [Sentinel Hub](https://www.sentinel-hub.com/)
- Built with [SentinelHub Python API](https://github.com/sentinel-hub/sentinelhub-py)
- Geometry operations powered by [Shapely](https://shapely.readthedocs.io/)

## Support
For issues or feature requests, please [open an issue](https://github.com/yourusername/sentinel-overlap-tool/issues).

---

**Note**: Replace all `yourusername` references with your actual GitHub username and credentials with your Sentinel Hub credentials before use.
```

```text
# Example Configure Sentinel Hub credentials (its a sample credential, doesn't work though.)
config = SHConfig()
config.sh_client_id = "sh-297e871c-8aec-801b-9d71-af5fbbb85446"
config.sh_client_secret = "6revR8Gyn666bZw5W6Eba4aLAlqOuKU8"
config.instance_id = "614d171f-4c1e-4a61-a158-88d01d0ce6d6"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
collection_l1c = DataCollection.SENTINEL2_L1C.define_from("s2l1c", service_url=config.sh_base_url)
collection_des = DataCollection.SENTINEL1_IW_DES.define_from("s1des", service_url=config.sh_base_url)
collection_asc = DataCollection.SENTINEL1_IW_ASC.define_from("s1asc", service_url=config.sh_base_url)

```

This README includes:
1. Clear installation instructions
2. Usage examples with parameter explanations
3. Sample output visualization
4. License and attribution information
5. Support information
6. Responsive badges and formatting

You'll also need a `requirements.txt` file:
```text
sentinelhub>=3.9.1
shapely>=2.0.1
pyproj>=3.6.0
python-dotenv>=1.0.0
geopandas>=0.13.0
argparse>=1.4.0
```

