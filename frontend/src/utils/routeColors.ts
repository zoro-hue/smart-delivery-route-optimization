/**
 * ROUTE/IQ Centralized Deterministic Route & Algorithm Color Management System
 * 
 * Single Source of Truth for Algorithm-Specific Base Color Families and
 * Vehicle Route Shades across the Results Workspace Map and Schedules.
 * 
 * Rules:
 * 1. Each algorithm has a distinct, stable base color family.
 * 2. Each vehicle route within an algorithm uses a distinct shade within that family.
 * 3. Stable across renders, page refreshes, and asynchronous updates.
 * 4. High-contrast legibility in both light and dark map viewports.
 * 5. Dynamic support for arbitrary fleet sizes (N vehicles).
 */

export interface VehicleRouteStyle {
  color: string;
  contrastTextColor: string;
  shadeName: string;
  dashArray?: string;
  familyName: string;
  baseColor: string;
}

export interface AlgorithmColorDefinition {
  id: string;
  name: string;
  familyName: string;
  baseColor: string;
  badgeBg: string;
  badgeText: string;
  border: string;
  lightShades: string[];
  darkShades: string[];
  shadeNames: string[];
}

/**
 * 11 Standardized Algorithm Base Color Families:
 * 
 * 1. ROUTE/IQ Cooperative Engine: Green Family
 * 2. OR-Tools (and classical): Blue Family
 * 3. QAOA: Purple Family
 * 4. QIGA: Magenta / Pink Family
 * 5. Tabu Search: Orange Family
 * 6. Clarke-Wright: Teal Family
 * 7. 2-opt: Yellow / Amber Family
 * 8. Kernighan-Lin: Rose / Crimson Family
 * 9. Variable Neighborhood Descent (VND): Indigo Family
 * 10. A*: Cyan / Sky Blue Family
 * 11. Dijkstra: Bronze / Slate Family
 */
export const ALGORITHM_COLOR_FAMILIES: Record<string, AlgorithmColorDefinition> = {
  routeiq_cooperative: {
    id: 'routeiq_cooperative',
    name: 'ROUTE/IQ Cooperative Engine',
    familyName: 'Green',
    baseColor: '#10B981',
    badgeBg: 'bg-emerald-500/15',
    badgeText: 'text-emerald-600 dark:text-emerald-400',
    border: 'border-emerald-500/40',
    lightShades: [
      '#065F46', // V1: Dark Green
      '#047857', // V2: Forest Green
      '#059669', // V3: Medium Green
      '#10B981', // V4: Vibrant Green
      '#16A34A', // V5: Leaf Green
      '#22C55E', // V6: Lime Green
      '#34D399', // V7: Pale Mint Green
      '#65A30D', // V8: Olive Green
    ],
    darkShades: [
      '#059669', // V1: Darker Green
      '#10B981', // V2: Emerald Green
      '#34D399', // V3: Medium Mint
      '#B7FF2A', // V4: Electric Lime
      '#4ADE80', // V5: Light Green
      '#6EE7B7', // V6: Pale Mint
      '#A7F3D0', // V7: Soft Sage
      '#84CC16', // V8: Bright Lime
    ],
    shadeNames: [
      'Dark Green',
      'Forest Green',
      'Medium Green',
      'Vibrant Green',
      'Leaf Green',
      'Lime Green',
      'Pale Mint',
      'Olive Green',
    ],
  },

  ortools: {
    id: 'ortools',
    name: 'OR-Tools',
    familyName: 'Blue',
    baseColor: '#2563EB',
    badgeBg: 'bg-blue-500/15',
    badgeText: 'text-blue-600 dark:text-blue-400',
    border: 'border-blue-500/40',
    lightShades: [
      '#1E3A8A', // V1: Dark Blue
      '#1D4ED8', // V2: Royal Blue
      '#2563EB', // V3: Medium Blue
      '#3B82F6', // V4: Light Blue
      '#4F46E5', // V5: Blue-Violet
      '#60A5FA', // V6: Pale Blue
      '#0284C7', // V7: Sky Blue
      '#93C5FD', // V8: Ice Blue
    ],
    darkShades: [
      '#1D4ED8', // V1: Deep Blue
      '#2563EB', // V2: Royal Blue
      '#3B82F6', // V3: Medium Blue
      '#60A5FA', // V4: Light Blue
      '#818CF8', // V5: Blue-Violet
      '#93C5FD', // V6: Pale Blue
      '#38BDF8', // V7: Sky Blue
      '#BFDBFE', // V8: Soft Ice Blue
    ],
    shadeNames: [
      'Dark Blue',
      'Royal Blue',
      'Medium Blue',
      'Light Blue',
      'Blue-Violet',
      'Pale Blue',
      'Sky Blue',
      'Ice Blue',
    ],
  },

  classical: {
    id: 'classical',
    name: 'OR-Tools (Classical)',
    familyName: 'Blue',
    baseColor: '#2563EB',
    badgeBg: 'bg-blue-500/15',
    badgeText: 'text-blue-600 dark:text-blue-400',
    border: 'border-blue-500/40',
    lightShades: [
      '#1E3A8A',
      '#1D4ED8',
      '#2563EB',
      '#3B82F6',
      '#4F46E5',
      '#60A5FA',
      '#0284C7',
      '#93C5FD',
    ],
    darkShades: [
      '#1D4ED8',
      '#2563EB',
      '#3B82F6',
      '#60A5FA',
      '#818CF8',
      '#93C5FD',
      '#38BDF8',
      '#BFDBFE',
    ],
    shadeNames: [
      'Dark Blue',
      'Royal Blue',
      'Medium Blue',
      'Light Blue',
      'Blue-Violet',
      'Pale Blue',
      'Sky Blue',
      'Ice Blue',
    ],
  },

  qaoa: {
    id: 'qaoa',
    name: 'QAOA',
    familyName: 'Purple',
    baseColor: '#8B5CF6',
    badgeBg: 'bg-purple-500/15',
    badgeText: 'text-purple-600 dark:text-purple-400',
    border: 'border-purple-500/40',
    lightShades: [
      '#581C87', // V1: Dark Purple
      '#6D28D9', // V2: Deep Violet
      '#7C3AED', // V3: Medium Purple
      '#8B5CF6', // V4: Light Purple
      '#9333EA', // V5: Bright Purple
      '#A855F7', // V6: Lavender
      '#C084FC', // V7: Pale Lilac
      '#DDD6FE', // V8: Soft Violet
    ],
    darkShades: [
      '#7C3AED', // V1: Deep Purple
      '#8B5CF6', // V2: Medium Purple
      '#A78BFA', // V3: Light Violet
      '#C4B5FD', // V4: Lavender
      '#C084FC', // V5: Bright Purple
      '#DDD6FE', // V6: Pale Lilac
      '#A855F7', // V7: Orchid
      '#EDE9FE', // V8: Whisper Violet
    ],
    shadeNames: [
      'Dark Purple',
      'Deep Violet',
      'Medium Purple',
      'Light Purple',
      'Bright Purple',
      'Lavender',
      'Pale Lilac',
      'Soft Violet',
    ],
  },

  qiga: {
    id: 'qiga',
    name: 'QIGA',
    familyName: 'Magenta / Pink',
    baseColor: '#D946EF',
    badgeBg: 'bg-fuchsia-500/15',
    badgeText: 'text-fuchsia-600 dark:text-fuchsia-400',
    border: 'border-fuchsia-500/40',
    lightShades: [
      '#701A75', // V1: Dark Magenta
      '#86198F', // V2: Deep Plum
      '#A21CAF', // V3: Medium Fuchsia
      '#C026D3', // V4: Hot Pink
      '#D946EF', // V5: Bright Magenta
      '#E879F9', // V6: Rose Pink
      '#F472B6', // V7: Pale Pink
      '#FBCFE8', // V8: Blush Pink
    ],
    darkShades: [
      '#A21CAF', // V1: Deep Magenta
      '#C026D3', // V2: Fuchsia
      '#D946EF', // V3: Bright Magenta
      '#E879F9', // V4: Electric Pink
      '#F0ABFC', // V5: Light Pink
      '#F472B6', // V6: Rose Pink
      '#F5D0FE', // V7: Pale Blush
      '#FDF2F8', // V8: Soft Blush
    ],
    shadeNames: [
      'Dark Magenta',
      'Deep Plum',
      'Medium Fuchsia',
      'Hot Pink',
      'Bright Magenta',
      'Rose Pink',
      'Pale Pink',
      'Blush Pink',
    ],
  },

  tabu_search: {
    id: 'tabu_search',
    name: 'Tabu Search',
    familyName: 'Orange',
    baseColor: '#F97316',
    badgeBg: 'bg-orange-500/15',
    badgeText: 'text-orange-600 dark:text-orange-400',
    border: 'border-orange-500/40',
    lightShades: [
      '#7C2D12', // V1: Dark Rust
      '#9A3412', // V2: Burnt Orange
      '#C2410C', // V3: Medium Orange
      '#EA580C', // V4: Tangerine
      '#F97316', // V5: Bright Orange
      '#FB923C', // V6: Coral Orange
      '#FDBA74', // V7: Pale Peach
      '#FED7AA', // V8: Warm Apricot
    ],
    darkShades: [
      '#C2410C', // V1: Deep Orange
      '#EA580C', // V2: Tangerine
      '#F97316', // V3: Bright Orange
      '#FB923C', // V4: Coral Orange
      '#FDBA74', // V5: Light Peach
      '#FED7AA', // V6: Pale Apricot
      '#FF8C42', // V7: Warm Peach
      '#FFEDD5', // V8: Cream Orange
    ],
    shadeNames: [
      'Dark Rust',
      'Burnt Orange',
      'Medium Orange',
      'Tangerine',
      'Bright Orange',
      'Coral Orange',
      'Pale Peach',
      'Warm Apricot',
    ],
  },

  clarke_wright: {
    id: 'clarke_wright',
    name: 'Clarke–Wright Savings',
    familyName: 'Teal',
    baseColor: '#14B8A6',
    badgeBg: 'bg-teal-500/15',
    badgeText: 'text-teal-600 dark:text-teal-400',
    border: 'border-teal-500/40',
    lightShades: [
      '#134E4A', // V1: Dark Teal
      '#115E59', // V2: Deep Pine Teal
      '#0F766E', // V3: Medium Teal
      '#0D9488', // V4: Aqua Teal
      '#14B8A6', // V5: Bright Teal
      '#2DD4BF', // V6: Seafoam Teal
      '#5EEAD4', // V7: Pale Aqua
      '#99F6E4', // V8: Ice Teal
    ],
    darkShades: [
      '#0D9488', // V1: Deep Teal
      '#14B8A6', // V2: Medium Teal
      '#2DD4BF', // V3: Seafoam Teal
      '#5EEAD4', // V4: Bright Aqua
      '#99F6E4', // V5: Pale Aqua
      '#A7F3D0', // V6: Light Mint
      '#CCFBF1', // V7: Ice Teal
      '#E6FFFA', // V8: Whisper Teal
    ],
    shadeNames: [
      'Dark Teal',
      'Deep Pine Teal',
      'Medium Teal',
      'Aqua Teal',
      'Bright Teal',
      'Seafoam Teal',
      'Pale Aqua',
      'Ice Teal',
    ],
  },

  two_opt: {
    id: 'two_opt',
    name: '2-opt',
    familyName: 'Yellow / Amber',
    baseColor: '#F59E0B',
    badgeBg: 'bg-amber-500/15',
    badgeText: 'text-amber-600 dark:text-amber-400',
    border: 'border-amber-500/40',
    lightShades: [
      '#78350F', // V1: Dark Amber
      '#92400E', // V2: Deep Bronze Amber
      '#B45309', // V3: Medium Amber
      '#D97706', // V4: Golden Amber
      '#F59E0B', // V5: Bright Amber
      '#FBBF24', // V6: Sunflower Yellow
      '#FCD34D', // V7: Pale Gold
      '#FEF3C7', // V8: Lemon Cream
    ],
    darkShades: [
      '#B45309', // V1: Deep Gold
      '#D97706', // V2: Golden Amber
      '#F59E0B', // V3: Bright Amber
      '#FBBF24', // V4: Sunflower Yellow
      '#FCD34D', // V5: Light Gold
      '#FEF3C7', // V6: Pale Butter
      '#FDE68A', // V7: Warm Glow
      '#FFFBEB', // V8: Lemon Silk
    ],
    shadeNames: [
      'Dark Amber',
      'Deep Bronze Amber',
      'Medium Amber',
      'Golden Amber',
      'Bright Amber',
      'Sunflower Yellow',
      'Pale Gold',
      'Lemon Cream',
    ],
  },

  kernighan_lin: {
    id: 'kernighan_lin',
    name: 'Kernighan–Lin',
    familyName: 'Rose / Crimson',
    baseColor: '#F43F5E',
    badgeBg: 'bg-rose-500/15',
    badgeText: 'text-rose-600 dark:text-rose-400',
    border: 'border-rose-500/40',
    lightShades: [
      '#881337', // V1: Dark Crimson
      '#9F1239', // V2: Ruby Red
      '#BE123C', // V3: Deep Rose
      '#E11D48', // V4: Medium Rose
      '#F43F5E', // V5: Bright Rose
      '#FB7185', // V6: Coral Rose
      '#FDA4AF', // V7: Pale Blossom
      '#FECDD3', // V8: Soft Blush
    ],
    darkShades: [
      '#BE123C', // V1: Deep Rose
      '#E11D48', // V2: Ruby Red
      '#F43F5E', // V3: Bright Rose
      '#FB7185', // V4: Coral Rose
      '#FDA4AF', // V5: Light Rose
      '#FECDD3', // V6: Pale Blossom
      '#FFE4E6', // V7: Warm Blush
      '#FFF1F2', // V8: Soft Rose
    ],
    shadeNames: [
      'Dark Crimson',
      'Ruby Red',
      'Deep Rose',
      'Medium Rose',
      'Bright Rose',
      'Coral Rose',
      'Pale Blossom',
      'Soft Blush',
    ],
  },

  vnd: {
    id: 'vnd',
    name: 'Variable Neighborhood Descent (VND)',
    familyName: 'Indigo',
    baseColor: '#6366F1',
    badgeBg: 'bg-indigo-500/15',
    badgeText: 'text-indigo-600 dark:text-indigo-400',
    border: 'border-indigo-500/40',
    lightShades: [
      '#312E81', // V1: Dark Midnight Indigo
      '#3730A3', // V2: Deep Indigo
      '#4338CA', // V3: Royal Indigo
      '#4F46E5', // V4: Medium Indigo
      '#6366F1', // V5: Bright Indigo
      '#818CF8', // V6: Periwinkle
      '#A5B4FC', // V7: Pale Periwinkle
      '#C7D2FE', // V8: Soft Lavender Blue
    ],
    darkShades: [
      '#4338CA', // V1: Deep Indigo
      '#4F46E5', // V2: Royal Indigo
      '#6366F1', // V3: Bright Indigo
      '#818CF8', // V4: Periwinkle
      '#A5B4FC', // V5: Light Periwinkle
      '#C7D2FE', // V6: Pale Periwinkle
      '#E0E7FF', // V7: Soft Lavender Blue
      '#EEF2FF', // V8: Whisper Indigo
    ],
    shadeNames: [
      'Dark Midnight Indigo',
      'Deep Indigo',
      'Royal Indigo',
      'Medium Indigo',
      'Bright Indigo',
      'Periwinkle',
      'Pale Periwinkle',
      'Soft Lavender Blue',
    ],
  },

  astar: {
    id: 'astar',
    name: 'A*',
    familyName: 'Cyan / Sky Blue',
    baseColor: '#06B6D4',
    badgeBg: 'bg-cyan-500/15',
    badgeText: 'text-cyan-600 dark:text-cyan-400',
    border: 'border-cyan-500/40',
    lightShades: [
      '#164E63', // V1: Dark Deep Cyan
      '#155E75', // V2: Deep Ocean Cyan
      '#0E7490', // V3: Medium Cyan
      '#0891B2', // V4: Cerulean Cyan
      '#06B6D4', // V5: Bright Cyan
      '#22D3EE', // V6: Electric Cyan
      '#67E8F9', // V7: Pale Sky Cyan
      '#A5F3FC', // V8: Ice Cyan
    ],
    darkShades: [
      '#0E7490', // V1: Deep Cyan
      '#0891B2', // V2: Cerulean Cyan
      '#06B6D4', // V3: Bright Cyan
      '#22D3EE', // V4: Electric Cyan
      '#67E8F9', // V5: Pale Sky Cyan
      '#A5F3FC', // V6: Light Ice Cyan
      '#CFFAFE', // V7: Soft Glacier
      '#ECFEFF', // V8: Frost Cyan
    ],
    shadeNames: [
      'Dark Deep Cyan',
      'Deep Ocean Cyan',
      'Medium Cyan',
      'Cerulean Cyan',
      'Bright Cyan',
      'Electric Cyan',
      'Pale Sky Cyan',
      'Ice Cyan',
    ],
  },

  dijkstra: {
    id: 'dijkstra',
    name: 'Dijkstra',
    familyName: 'Bronze / Slate',
    baseColor: '#78716C',
    badgeBg: 'bg-stone-500/15',
    badgeText: 'text-stone-600 dark:text-stone-300',
    border: 'border-stone-500/40',
    lightShades: [
      '#44403C', // V1: Dark Espresso Bronze
      '#57534E', // V2: Umber Bronze
      '#78716C', // V3: Warm Stone
      '#A8A29E', // V4: Medium Stone
      '#D6D3D1', // V5: Pale Taupe
      '#71717A', // V6: Slate Bronze
      '#A1A1AA', // V7: Light Slate
      '#E4E4E7', // V8: Soft Pebble
    ],
    darkShades: [
      '#57534E', // V1: Deep Stone
      '#78716C', // V2: Warm Stone
      '#A8A29E', // V3: Light Stone
      '#D6D3D1', // V4: Pale Taupe
      '#E7E5E4', // V5: Soft Sand
      '#A1A1AA', // V6: Light Slate
      '#D4D4D8', // V7: Silver Slate
      '#F4F4F5', // V8: Whisper Stone
    ],
    shadeNames: [
      'Dark Espresso Bronze',
      'Umber Bronze',
      'Warm Stone',
      'Medium Stone',
      'Pale Taupe',
      'Slate Bronze',
      'Light Slate',
      'Soft Pebble',
    ],
  },
};

/**
 * Calculates high-contrast text color (#080808 or #FFFFFF) based on hex luminance.
 */
export function getContrastTextColor(hex: string): string {
  try {
    const cleanHex = hex.replace('#', '');
    const r = parseInt(cleanHex.substring(0, 2), 16) || 0;
    const g = parseInt(cleanHex.substring(2, 4), 16) || 0;
    const b = parseInt(cleanHex.substring(4, 6), 16) || 0;
    // Relative luminance calculation
    const yiq = (r * 299 + g * 587 + b * 114) / 1000;
    return yiq >= 145 ? '#080808' : '#FFFFFF';
  } catch {
    return '#FFFFFF';
  }
}

/**
 * Returns canonical display name for an algorithm ID.
 */
export function getAlgorithmDisplayName(id: string, rawName?: string): string {
  const normId = normalizeAlgorithmId(id);
  if (normId === 'routeiq_cooperative') return 'ROUTE/IQ Cooperative Engine';
  if (normId === 'qaoa') return 'QAOA (Quantum Approximate Optimization)';
  if (normId === 'qiga') return 'QIGA (Quantum-Inspired GA)';
  if (normId === 'ortools' || normId === 'classical') return 'OR-Tools';
  if (normId === 'clarke_wright') return 'Clarke–Wright Savings';
  if (normId === 'two_opt') return '2-opt Improvement';
  if (normId === 'tabu_search') return 'Tabu Search';
  if (normId === 'kernighan_lin') return 'Kernighan–Lin';
  if (normId === 'vnd') return 'Variable Neighborhood Descent (VND)';
  if (normId === 'astar') return 'A*';
  if (normId === 'dijkstra') return 'Dijkstra';
  return rawName || id;
}

/**
 * Normalizes algorithm key aliases (e.g. 'classical' -> 'ortools').
 */
export function normalizeAlgorithmId(id?: string): string {
  if (!id) return 'ortools';
  const lower = id.toLowerCase().trim();
  if (lower === 'classical') return 'ortools';
  if (lower.includes('cooperative')) return 'routeiq_cooperative';
  if (lower.includes('qaoa')) return 'qaoa';
  if (lower.includes('qiga')) return 'qiga';
  if (lower.includes('clarke')) return 'clarke_wright';
  if (lower.includes('tabu')) return 'tabu_search';
  if (lower.includes('two_opt') || lower.includes('2-opt') || lower.includes('2opt')) return 'two_opt';
  if (lower.includes('kernighan')) return 'kernighan_lin';
  if (lower.includes('vnd')) return 'vnd';
  if (lower.includes('astar') || lower.includes('a*')) return 'astar';
  if (lower.includes('dijkstra')) return 'dijkstra';
  if (ALGORITHM_COLOR_FAMILIES[lower]) return lower;
  return 'ortools';
}

export interface VehicleColorDefinition {
  id: number;
  name: string;
  lightColor: string;
  darkColor: string;
}

/**
 * Standard High-Contrast Multi-Vehicle Palette:
 *
 * Vehicle 1: Blue
 * Vehicle 2: Orange
 * Vehicle 3: Purple
 * Vehicle 4: Teal
 * Vehicle 5: Pink
 * Vehicle 6: Yellow
 * Vehicle 7: Emerald Green
 * Vehicle 8: Indigo
 * Vehicle 9: Red
 * Vehicle 10: Cyan
 * Vehicle 11: Fuchsia
 * Vehicle 12: Lime
 */
export const VEHICLE_PALETTE: VehicleColorDefinition[] = [
  { id: 1, name: 'Blue', lightColor: '#2563EB', darkColor: '#3B82F6' },
  { id: 2, name: 'Orange', lightColor: '#EA580C', darkColor: '#F97316' },
  { id: 3, name: 'Purple', lightColor: '#9333EA', darkColor: '#A855F7' },
  { id: 4, name: 'Teal', lightColor: '#0D9488', darkColor: '#14B8A6' },
  { id: 5, name: 'Pink', lightColor: '#DB2777', darkColor: '#EC4899' },
  { id: 6, name: 'Yellow', lightColor: '#D97706', darkColor: '#F59E0B' },
  { id: 7, name: 'Emerald', lightColor: '#059669', darkColor: '#10B981' },
  { id: 8, name: 'Indigo', lightColor: '#4F46E5', darkColor: '#6366F1' },
  { id: 9, name: 'Red', lightColor: '#DC2626', darkColor: '#EF4444' },
  { id: 10, name: 'Cyan', lightColor: '#0284C7', darkColor: '#06B6D4' },
  { id: 11, name: 'Fuchsia', lightColor: '#C026D3', darkColor: '#D946EF' },
  { id: 12, name: 'Lime', lightColor: '#65A30D', darkColor: '#84CC16' },
];

/**
 * Line dash patterns for vehicle counts exceeding base shade tiers (N > 12)
 * to ensure overlapping or dense multi-vehicle routes remain distinct.
 */
const FALLBACK_DASH_PATTERNS = [
  undefined,
  '5, 5',
  '8, 4',
  '3, 3',
  '10, 4, 2, 4',
  '6, 3, 2, 3',
];

/**
 * Returns deterministic styling for a specific vehicle route belonging to an algorithm.
 *
 * Rules:
 * - Each vehicle has a distinct, visually distinguishable color (Vehicle 1: Blue, Vehicle 2: Orange, etc.).
 * - Stable across algorithm switches, refreshes, and async results.
 * - Same vehicle ID retains the same color across algorithms.
 * - Dynamic support for any fleet size.
 *
 * @param algorithmId - ID or alias of the algorithm (optional context)
 * @param vehicleIndexOrId - 0-based index or 1-based vehicle ID
 * @param isDark - whether dark mode theme is active
 * @param totalVehicles - total number of vehicles in fleet (optional)
 */
export function getVehicleRouteStyle(
  algorithmId: string,
  vehicleIndexOrId: number | string,
  isDark: boolean,
  totalVehicles: number = 5
): VehicleRouteStyle {
  // Derive stable 0-based index and 1-based vehicle number
  let idx = 0;
  if (typeof vehicleIndexOrId === 'number') {
    idx = vehicleIndexOrId >= 1 ? vehicleIndexOrId - 1 : vehicleIndexOrId;
  } else if (typeof vehicleIndexOrId === 'string') {
    const match = vehicleIndexOrId.match(/\d+/);
    idx = match ? parseInt(match[0], 10) - 1 : 0;
  }
  idx = Math.max(0, idx);
  const vehicleNumber = idx + 1;

  const numColors = VEHICLE_PALETTE.length;
  const colorIndex = idx % numColors;
  const cycleIndex = Math.floor(idx / numColors);

  const def = VEHICLE_PALETTE[colorIndex];
  const color = isDark ? def.darkColor : def.lightColor;
  const contrastTextColor = getContrastTextColor(color);
  const baseName = def.name;
  const shadeName = cycleIndex > 0 ? `${baseName} (Tier ${cycleIndex + 1})` : baseName;

  // Use line pattern distinctions if vehicle count exceeds available shades or for high vehicle density
  let dashArray: string | undefined = undefined;
  if (cycleIndex > 0) {
    dashArray = FALLBACK_DASH_PATTERNS[cycleIndex % FALLBACK_DASH_PATTERNS.length];
  } else if (totalVehicles > 6 && idx % 2 === 1) {
    dashArray = '6, 4';
  }

  return {
    color,
    contrastTextColor,
    shadeName,
    dashArray,
    familyName: `Vehicle ${vehicleNumber}`,
    baseColor: color,
  };
}

/**
 * Returns the full palette of vehicle colors for a given algorithm and theme.
 */
export function getAlgorithmVehicleColors(
  algorithmId: string,
  isDark: boolean,
  count: number = 8
): string[] {
  const result: string[] = [];
  for (let i = 0; i < count; i++) {
    result.push(getVehicleRouteStyle(algorithmId, i, isDark, count).color);
  }
  return result;
}
