/**
 * Geospatial Validation Utility for ROUTE/IQ Logistics Engine
 * Detects water bodies (Hudson River, East River, Upper/Lower NY Bay,
 * Atlantic Ocean, Jamaica Bay, Long Island Sound, Newark Bay)
 * and verifies geographic boundary constraints for vehicle routing.
 */

// Point in polygon ray-casting test
export function isPointInPolygon(
  point: [number, number],
  polygon: [number, number][]
): boolean {
  const [lat, lon] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const intersect =
      yi > lon !== yj > lon &&
      lat < ((xj - xi) * (lon - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

interface WaterBodyDefinition {
  id: string;
  name: string;
  polygon?: [number, number][];
  box?: { minLat: number; maxLat: number; minLon: number; maxLon: number };
  condition?: (lat: number, lon: number) => boolean;
}

export const NYC_WATER_BODIES: WaterBodyDefinition[] = [
  // 1. Hudson River (between Manhattan & New Jersey)
  {
    id: 'hudson_river',
    name: 'Hudson River',
    polygon: [
      [40.7020, -74.0200],
      [40.7080, -74.0195],
      [40.7200, -74.0170],
      [40.7400, -74.0130],
      [40.7600, -74.0070],
      [40.7850, -73.9890],
      [40.8150, -73.9660],
      [40.8500, -73.9420],
      [40.8850, -73.9210],
      [40.9100, -73.9100],
      [40.9100, -73.9350],
      [40.8850, -73.9480],
      [40.8500, -73.9680],
      [40.8150, -73.9890],
      [40.7850, -74.0100],
      [40.7600, -74.0240],
      [40.7400, -74.0290],
      [40.7200, -74.0320],
      [40.7050, -74.0330],
      [40.7000, -74.0250],
    ],
  },

  // 2. Lower East River (between Downtown Manhattan and Brooklyn / Queens)
  {
    id: 'lower_east_river',
    name: 'East River',
    polygon: [
      [40.6980, -74.0150],
      [40.7060, -73.9980],
      [40.7100, -73.9880],
      [40.7180, -73.9720],
      [40.7300, -73.9680],
      [40.7420, -73.9600],
      [40.7520, -73.9530],
      [40.7550, -73.9450],
      [40.7450, -73.9490],
      [40.7320, -73.9570],
      [40.7190, -73.9630],
      [40.7080, -73.9780],
      [40.7000, -73.9910],
      [40.6930, -74.0040],
    ],
  },

  // 3. Upper East River & Hell Gate / Long Island Sound connection
  {
    id: 'upper_east_river',
    name: 'Upper East River / Hell Gate',
    polygon: [
      [40.7550, -73.9550],
      [40.7720, -73.9400],
      [40.7880, -73.9240],
      [40.8050, -73.8950],
      [40.8120, -73.8650],
      [40.8160, -73.8150],
      [40.8030, -73.8150],
      [40.7950, -73.8650],
      [40.7920, -73.8900],
      [40.7770, -73.9180],
      [40.7630, -73.9350],
      [40.7520, -73.9480],
    ],
  },

  // 4. Upper New York Bay (South of Manhattan tip, between Brooklyn & NJ)
  {
    id: 'upper_ny_bay',
    name: 'Upper New York Bay',
    polygon: [
      [40.7020, -74.0220],
      [40.6950, -74.0150],
      [40.6750, -74.0200],
      [40.6480, -74.0380],
      [40.6380, -74.0480],
      [40.6400, -74.0720],
      [40.6600, -74.0800],
      [40.6800, -74.0650],
      [40.6980, -74.0400],
    ],
  },

  // 5. The Narrows (Waterway connecting Upper and Lower NY Bay)
  {
    id: 'the_narrows',
    name: 'The Narrows',
    polygon: [
      [40.6450, -74.0450],
      [40.6300, -74.0350],
      [40.6000, -74.0420],
      [40.6000, -74.0680],
      [40.6300, -74.0650],
      [40.6450, -74.0550],
    ],
  },

  // 6. Lower New York Bay & Atlantic Ocean
  {
    id: 'lower_ny_bay_atlantic',
    name: 'Atlantic Ocean / Lower NY Bay',
    condition: (lat, lon) => {
      // Anything south of latitude 40.550 is open ocean/Lower Bay
      if (lat < 40.550 && lon > -74.250 && lon < -73.700) return true;
      // Lower NY Bay triangular water section south of Brooklyn / Staten Island
      if (lat < 40.585 && lon >= -74.120 && lon <= -74.010) return true;
      // Ocean south of the Rockaways
      if (lat < 40.575 && lon >= -73.930 && lon <= -73.740) return true;
      return false;
    },
  },

  // 7. Jamaica Bay Interior Water
  {
    id: 'jamaica_bay',
    name: 'Jamaica Bay',
    polygon: [
      [40.6550, -73.8650],
      [40.6500, -73.8200],
      [40.6350, -73.8100],
      [40.6100, -73.8150],
      [40.5950, -73.8450],
      [40.5980, -73.8800],
      [40.6250, -73.8850],
      [40.6450, -73.8750],
    ],
  },

  // 8. Long Island Sound / Eastchester Bay coastal water
  {
    id: 'long_island_sound',
    name: 'Long Island Sound',
    condition: (lat, lon) => {
      if (lat >= 40.810 && lon >= -73.770) return true;
      if (lat >= 40.835 && lon >= -73.800) return true;
      return false;
    },
  },

  // 9. Newark Bay & Kill Van Kull
  {
    id: 'newark_bay',
    name: 'Newark Bay / Kill Van Kull',
    polygon: [
      [40.7150, -74.1350],
      [40.6800, -74.1200],
      [40.6480, -74.1250],
      [40.6420, -74.0850],
      [40.6340, -74.0850],
      [40.6380, -74.1400],
      [40.6650, -74.1450],
      [40.7100, -74.1500],
    ],
  },

  // 10. Arthur Kill (West of Staten Island)
  {
    id: 'arthur_kill',
    name: 'Arthur Kill',
    polygon: [
      [40.6350, -74.2050],
      [40.6000, -74.1950],
      [40.5600, -74.2150],
      [40.5100, -74.2500],
      [40.5050, -74.2600],
      [40.5400, -74.2400],
      [40.5850, -74.2250],
      [40.6300, -74.2200],
    ],
  },


  {
    id: 'upper_ny_bay_corridor',
    name: 'Upper New York Bay',
    condition: (lat, lon) => {
      // Open water south of Governors Island / Battery Park, between Brooklyn and Jersey City / Bayonne
      return lat >= 40.635 && lat <= 40.705 && lon >= -74.075 && lon <= -74.020;
    },
  },
  {
    id: 'jamaica_bay_corridor',
    name: 'Jamaica Bay',
    condition: (lat, lon) => {
      // Open waters inside Jamaica Bay
      return lat >= 40.590 && lat <= 40.660 && lon >= -73.880 && lon <= -73.810;
    },
  },
  {
    id: 'ocean_corridor',
    name: 'Atlantic Ocean / Lower Bay',
    condition: (lat, lon) => {
      // South of Coney Island, Rockaways, and Lower Bay
      if (lat < 40.565 && lon >= -74.150 && lon <= -73.730) return true;
      // Outer coastal waters
      if (lat < 40.575 && lon >= -73.950 && lon <= -73.740) return true;
      return false;
    },
  },
];

export interface GeoValidationResult {
  isValid: boolean;
  error?: string;
  waterBodyName?: string;
}

/**
 * Validates a coordinate for ground delivery routing.
 * Ensures the coordinate is not inside a water body and within the operational NYC metro bounds.
 */
export function validateDeliveryCoordinate(lat: number, lon: number): GeoValidationResult {
  // 1. Basic coordinate sanity
  if (isNaN(lat) || isNaN(lon)) {
    return { isValid: false, error: 'Coordinate numbers are invalid or empty.' };
  }
  if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
    return { isValid: false, error: 'Latitude must be between -90 and 90, Longitude between -180 and 180.' };
  }

  // 2. Metropolitan operational bounds
  // Nassau County / Long Island check (Queens eastern border is at lon -73.7005)
  if (lon > -73.7005) {
    return {
      isValid: false,
      error: `Coordinate (${lat.toFixed(4)}, ${lon.toFixed(4)}) is in Nassau County / Long Island, outside the active NYC 5-Borough road network (Manhattan, Brooklyn, Queens, Bronx, Staten Island).`,
    };
  }

  // Exclude New Jersey coordinates across Hudson River (lat > 40.70, lon < -74.02)
  if (lat > 40.70 && lon < -74.02) {
    return {
      isValid: false,
      error: `Coordinate (${lat.toFixed(4)}, ${lon.toFixed(4)}) is in New Jersey across the Hudson River. Fleet routing is localized to the NYC 5-Borough road network.`,
    };
  }

  // General NYC 5-Borough metropolitan bounds
  if (lat < 40.48 || lat > 40.95 || lon < -74.28) {
    return {
      isValid: false,
      error: `Coordinate (${lat.toFixed(4)}, ${lon.toFixed(4)}) is outside the active NYC 5-Borough dispatch area (Manhattan, Brooklyn, Queens, Bronx, Staten Island).`,
    };
  }

  // 3. Water body checks
  for (const wb of NYC_WATER_BODIES) {
    let isInWater = false;

    if (wb.condition && wb.condition(lat, lon)) {
      isInWater = true;
    } else if (wb.polygon && isPointInPolygon([lat, lon], wb.polygon)) {
      isInWater = true;
    } else if (wb.box) {
      if (
        lat >= wb.box.minLat &&
        lat <= wb.box.maxLat &&
        lon >= wb.box.minLon &&
        lon <= wb.box.maxLon
      ) {
        isInWater = true;
      }
    }

    if (isInWater) {
      return {
        isValid: false,
        waterBodyName: wb.name,
        error: `Cannot place delivery stop or depot in open water (${wb.name}). Road couriers and delivery vehicles require navigable roadways.`,
      };
    }
  }

  return { isValid: true };
}
