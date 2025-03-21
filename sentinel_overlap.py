import argparse
from datetime import datetime, timedelta
from sentinelhub import SHConfig, SentinelHubCatalog, Geometry, DataCollection
from shapely.geometry import Point
import pyproj
from shapely.geometry import Point, shape  
from shapely.ops import transform

# Configure Sentinel Hub credentials
config = SHConfig()
config.sh_client_id = "sh-297e871c-8aec-------------af5fbbb85446" #use your credentials 
config.sh_client_secret = "6revR8Gyn9---------W6Eba6aLAlqOuKU8" #use your credentials 
config.instance_id = "614d171f-9c1e-4----------78-88d01d0ce6d6" #use your credentials 
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
collection_l1c = DataCollection.SENTINEL2_L1C.define_from("s2l1c", service_url=config.sh_base_url)
collection_des = DataCollection.SENTINEL1_IW_DES.define_from("s1des", service_url=config.sh_base_url)
collection_asc = DataCollection.SENTINEL1_IW_ASC.define_from("s1asc", service_url=config.sh_base_url)
def parse_date(date_str):
    return datetime.strptime(date_str, "%d:%m:%y")

def create_search_area(lon, lat, buffer_degrees):
    """Create buffered search area with visualization"""
    point = Point(lon, lat)
    buffered = point.buffer(buffer_degrees)
    print(f"Search area: {buffered.wkt}")
    return buffered

def get_acquisitions(collection, geometry, start_date, end_date):
    """Get acquisitions with debug logging"""
    catalog = SentinelHubCatalog(config=config)
    search_geometry = Geometry(geometry.wkt, crs="EPSG:4326")
    
    print(f"\nSearching {collection.name} from {start_date} to {end_date}")
    
    results = list(catalog.search(
        collection=collection,
        geometry=search_geometry,
        time=(start_date, end_date),
        fields={"include": ["id", "properties.datetime", "geometry", "properties.cloudCover"]}
    ))
    
    print(f"Found {len(results)} raw acquisitions")
    return [{
        "time": datetime.fromisoformat(item["properties"]["datetime"]),
        "geometry": item["geometry"],
        "cloud_cover": item["properties"].get("cloudCover", 0)
    } for item in results]

def calculate_overlap(geom1, geom2):
    """Calculate spatial overlap percentage with proper error handling"""
    try:
        # Convert GeoJSON geometries to Shapely objects
        poly1 = shape(geom1)
        poly2 = shape(geom2)
        
        # Get UTM zone for coordinate system transformation
        centroid_x = poly1.centroid.x
        utm_zone = int((centroid_x + 180)/6) + 1
        utm_crs = pyproj.CRS(f'EPSG:326{utm_zone}')
        
        # Create coordinate transformer
        transformer = pyproj.Transformer.from_crs(
            pyproj.CRS('EPSG:4326'), 
            utm_crs, 
            always_xy=True
        )
        
        # Transform geometries to UTM
        poly1_utm = transform(transformer.transform, poly1)
        poly2_utm = transform(transformer.transform, poly2)
        
        # Calculate intersection
        intersection = poly1_utm.intersection(poly2_utm)
        if intersection.is_empty:
            return 0.0
            
        # Calculate overlap percentage
        overlap_pct = (intersection.area / poly1_utm.area) * 100
        return round(overlap_pct, 2)

    except Exception as e:
        print(f"\nOverlap calculation error details:")
        print(f"- Geometry 1: {geom1}")
        print(f"- Geometry 2: {geom2}")
        print(f"- Error message: {str(e)}")
        return 0.0

def main():
    parser = argparse.ArgumentParser(description='Find Sentinel acquisition overlaps')
    parser.add_argument('latitude', type=float, help='Latitude (decimal degrees)')
    parser.add_argument('longitude', type=float, help='Longitude (decimal degrees)')
    parser.add_argument('start_date', type=parse_date, help='Start date (dd:mm:yy)')
    parser.add_argument('end_date', type=parse_date, help='End date (dd:mm:yy)')
    parser.add_argument('--max-diff', type=int, default=180,
                      help='Max time difference in minutes (default: 3hrs)')
    parser.add_argument('--buffer', type=float, default=0.5,
                      help='Search buffer in degrees (default: 0.5° ≈ 55km)')
    parser.add_argument('--min-overlap', type=float, default=1.0,
                      help='Minimum spatial overlap percentage (default: 1%)')

    args = parser.parse_args()
    
    # Create search area
    search_area = create_search_area(args.longitude, args.latitude, args.buffer)
    
    # Get acquisitions with cloud cover filtering
    s1_acqs = get_acquisitions(DataCollection.SENTINEL1_IW, search_area, args.start_date, args.end_date)
    s2_acqs = get_acquisitions(DataCollection.SENTINEL2_L2A, search_area, args.start_date, args.end_date)
    
    print(f"\nSentinel-1 acquisitions: {len(s1_acqs)}")
    print(f"Sentinel-2 acquisitions: {len(s2_acqs)}")
    
    # Find overlaps
    max_delta = timedelta(minutes=args.max_diff)
    overlaps = []
    
    for s1 in s1_acqs:
        for s2 in s2_acqs:
            time_diff = abs(s1["time"] - s2["time"])
            if time_diff <= max_delta:
                overlap_pct = calculate_overlap(s1["geometry"], s2["geometry"])
                if overlap_pct >= args.min_overlap and s2["cloud_cover"] < 80:
                    overlaps.append({
                        "s1_time": s1["time"],
                        "s2_time": s2["time"],
                        "time_diff": time_diff,
                        "overlap_pct": round(overlap_pct, 2),
                        "cloud_cover": s2["cloud_cover"]
                    })
    # Print results
    print(f"\nFound {len(overlaps)} overlapping acquisitions between {args.start_date:%d-%b-%Y} and {args.end_date:%d-%b-%Y}")
    print(f"Location: {args.latitude:.4f}°N, {args.longitude:.4f}°E")
    print(f"Max time difference: {args.max_diff} mins | Min overlap: 0.01%")
    
    for idx, overlap in enumerate(overlaps, 1):
        print(f"\nOverlap {idx}:")
        print(f"  Sentinel-1: {overlap['s1_time'].strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  Sentinel-2: {overlap['s2_time'].strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  Δ Time: {overlap['time_diff'].total_seconds()/60:.1f} minutes")
        print(f"  Overlap Percentage: {overlap['overlap_pct']}%")

if __name__ == '__main__':
    main()
