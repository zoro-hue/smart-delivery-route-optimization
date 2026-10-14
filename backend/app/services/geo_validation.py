"""
Geospatial Water Body & Metropolitan Boundary Validator for ROUTE/IQ.
Prevents vehicle routing through water bodies (Hudson River, East River,
Upper/Lower New York Bay, Atlantic Ocean, Jamaica Bay, Long Island Sound).
"""

from typing import Tuple, List, Optional

def is_point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersect = ((yi > lon) != (yj > lon)) and (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside

# Water body polygons (lat, lon)
HUDSON_RIVER = [
    (40.7020, -74.0200), (40.7080, -74.0195), (40.7200, -74.0170), (40.7400, -74.0130),
    (40.7600, -74.0070), (40.7850, -73.9890), (40.8150, -73.9660), (40.8500, -73.9420),
    (40.8850, -73.9210), (40.9100, -73.9100), (40.9100, -73.9350), (40.8850, -73.9480),
    (40.8500, -73.9680), (40.8150, -73.9890), (40.7850, -74.0100), (40.7600, -74.0240),
    (40.7400, -74.0290), (40.7200, -74.0320), (40.7050, -74.0330), (40.7000, -74.0250)
]

LOWER_EAST_RIVER = [
    (40.6980, -74.0150), (40.7060, -73.9980), (40.7100, -73.9880), (40.7180, -73.9720),
    (40.7300, -73.9680), (40.7420, -73.9600), (40.7520, -73.9530), (40.7550, -73.9450),
    (40.7450, -73.9490), (40.7320, -73.9570), (40.7190, -73.9630), (40.7080, -73.9780),
    (40.7000, -73.9910), (40.6930, -74.0040)
]

UPPER_EAST_RIVER = [
    (40.7550, -73.9550), (40.7720, -73.9400), (40.7880, -73.9240), (40.8050, -73.8950),
    (40.8120, -73.8650), (40.8160, -73.8150), (40.8030, -73.8150), (40.7950, -73.8650),
    (40.7920, -73.8900), (40.7770, -73.9180), (40.7630, -73.9350), (40.7520, -73.9480)
]

UPPER_NY_BAY = [
    (40.7020, -74.0220), (40.6950, -74.0150), (40.6750, -74.0200), (40.6480, -74.0380),
    (40.6380, -74.0480), (40.640, -74.0720), (40.6600, -74.0800), (40.6800, -74.0650),
    (40.6980, -74.0400)
]

THE_NARROWS = [
    (40.6450, -74.0450), (40.6300, -74.0350), (40.6000, -74.0420), (40.6000, -74.0680),
    (40.6300, -74.0650), (40.6450, -74.0550)
]

JAMAICA_BAY = [
    (40.6550, -73.8650), (40.6500, -73.8200), (40.6350, -73.8100), (40.6100, -73.8150),
    (40.5950, -73.8450), (40.5980, -73.8800), (40.6250, -73.8850), (40.6450, -73.8750)
]

NEWARK_BAY = [
    (40.7150, -74.1350), (40.6800, -74.1200), (40.6480, -74.1250), (40.6420, -74.0850),
    (40.6340, -74.0850), (40.6380, -74.1400), (40.6650, -74.1450), (40.7100, -74.1500)
]

def check_water_body(lat: float, lon: float) -> Optional[str]:
    """Returns the water body name if (lat, lon) is in open water, or None if valid land."""
    # 1. Atlantic Ocean & Lower Bay
    if lat < 40.565 and -74.150 <= lon <= -73.730:
        return "Atlantic Ocean"
    if lat < 40.585 and -74.120 <= lon <= -74.010:
        return "Lower New York Bay"
    if lat < 40.575 and -73.950 <= lon <= -73.740:
        return "Atlantic Ocean"
    if lat >= 40.810 and lon >= -73.770:
        return "Long Island Sound"

    # 2. Detailed Water Body Polygons (precise shoreline ray-casting)
    if is_point_in_polygon(lat, lon, HUDSON_RIVER):
        return "Hudson River"
    if is_point_in_polygon(lat, lon, LOWER_EAST_RIVER):
        return "East River"
    if is_point_in_polygon(lat, lon, UPPER_EAST_RIVER):
        return "Upper East River / Hell Gate"
    if is_point_in_polygon(lat, lon, UPPER_NY_BAY):
        return "Upper New York Bay"
    if is_point_in_polygon(lat, lon, THE_NARROWS):
        return "The Narrows"
    if is_point_in_polygon(lat, lon, JAMAICA_BAY):
        return "Jamaica Bay"
    if is_point_in_polygon(lat, lon, NEWARK_BAY):
        return "Newark Bay"
    return None


def validate_nyc_coordinate(lat: float, lon: float) -> Tuple[bool, Optional[str]]:
    """
    Validates that a delivery stop or depot coordinate is within the active NYC 5-Borough road network
    and not located inside water bodies or adjacent non-service jurisdictions (New Jersey, Nassau County).
    Returns (is_valid, error_message).
    """
    import math
    if math.isnan(lat) or math.isnan(lon):
        return False, "Coordinate values are invalid or empty."

    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        return False, "Latitude must be between -90 and 90, Longitude between -180 and 180."

    # Water body check
    wb = check_water_body(lat, lon)
    if wb:
        return False, f"Cannot route across open water body ({wb}). Commercial vehicles require road-network infrastructure."

    # Nassau County / Long Island boundary (Queens eastern border is at lon -73.7005)
    if lon > -73.7005:
        return False, f"Coordinate ({lat:.4f}, {lon:.4f}) is in Nassau County / Long Island, outside the active NYC 5-Borough road network (Manhattan, Brooklyn, Queens, Bronx, Staten Island)."

    # New Jersey across Hudson River (lat > 40.70, lon < -74.02)
    if lat > 40.70 and lon < -74.02:
        return False, f"Coordinate ({lat:.4f}, {lon:.4f}) is in New Jersey across the Hudson River. Fleet routing is localized to the NYC 5-Borough road network."

    # General NYC 5-Borough metropolitan bounds
    if lat < 40.48 or lat > 40.95 or lon < -74.28:
        return False, f"Coordinate ({lat:.4f}, {lon:.4f}) is outside the active NYC 5-Borough dispatch area (Manhattan, Brooklyn, Queens, Bronx, Staten Island)."

    return True, None

