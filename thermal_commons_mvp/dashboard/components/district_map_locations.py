"""Singapore CBD building locations - 50 real buildings in Central Business District."""

from typing import Dict, Tuple

# Real CBD buildings in Singapore with approximate coordinates
# Centered around Marina Bay, Raffles Place, and Shenton Way
CBD_BUILDINGS = [
    # Marina Bay Financial Centre area
    ("Marina Bay Financial Centre Tower 1", 1.2803, 103.8544),
    ("Marina Bay Financial Centre Tower 2", 1.2808, 103.8548),
    ("Marina Bay Financial Centre Tower 3", 1.2812, 103.8552),
    ("Marina Bay Suites", 1.2805, 103.8550),
    ("Marina Bay Link Mall", 1.2800, 103.8540),
    
    # One Raffles Quay / Marina Bay area
    ("One Raffles Quay North Tower", 1.2811, 103.8515),
    ("One Raffles Quay South Tower", 1.2808, 103.8512),
    ("Asia Square Tower 1", 1.2805, 103.8518),
    ("Asia Square Tower 2", 1.2802, 103.8520),
    ("Marina Bay Residences", 1.2815, 103.8510),
    
    # Raffles Place core
    ("One Raffles Place Tower 1", 1.2843, 103.8511),
    ("One Raffles Place Tower 2", 1.2840, 103.8514),
    ("UOB Plaza One", 1.2836, 103.8515),
    ("UOB Plaza Two", 1.2838, 103.8517),
    ("OCBC Centre", 1.2834, 103.8513),
    ("Republic Plaza", 1.2832, 103.8516),
    ("Capital Tower", 1.2773, 103.8450),
    ("The Gateway", 1.2830, 103.8508),
    ("Standard Chartered Building", 1.2835, 103.8518),
    ("HSBC Building", 1.2833, 103.8512),
    
    # Shenton Way
    ("Shenton House", 1.2775, 103.8452),
    ("UIC Building", 1.2777, 103.8454),
    ("MAS Building", 1.2779, 103.8456),
    ("DBS Building Tower One", 1.2771, 103.8448),
    ("DBS Building Tower Two", 1.2770, 103.8446),
    ("AXA Tower", 1.2778, 103.8458),
    ("Robinson Point", 1.2776, 103.8460),
    ("Tower 15", 1.2774, 103.8462),
    ("SGX Centre", 1.2772, 103.8464),
    ("Shaw Tower", 1.2770, 103.8466),
    
    # Tanjong Pagar / Anson Road
    ("Tanjong Pagar Centre", 1.2800, 103.8300),
    ("Guoco Tower", 1.2802, 103.8302),
    ("International Plaza", 1.2804, 103.8304),
    ("Anson House", 1.2806, 103.8306),
    ("Tanjong Pagar Complex", 1.2808, 103.8308),
    ("PSA Building", 1.2810, 103.8310),
    ("Keppel Towers", 1.2812, 103.8312),
    ("Mapletree Business City", 1.2814, 103.8314),
    ("Alexandra Point", 1.2816, 103.8316),
    ("Harbourfront Tower One", 1.2818, 103.8318),
    
    # Marina Bay Sands / Esplanade area
    ("Marina Bay Sands Tower 1", 1.2820, 103.8580),
    ("Marina Bay Sands Tower 2", 1.2822, 103.8582),
    ("Marina Bay Sands Tower 3", 1.2824, 103.8584),
    ("The Shoppes at Marina Bay", 1.2826, 103.8586),
    ("Esplanade Theatres", 1.2894, 103.8500),
    ("Suntec City Tower 1", 1.2947, 103.8585),
    ("Suntec City Tower 2", 1.2950, 103.8587),
    ("Suntec City Tower 3", 1.2952, 103.8589),
    ("Suntec City Tower 4", 1.2954, 103.8591),
    ("Millenia Tower", 1.2930, 103.8570),
]

# Map Building_01 through Building_50 to real CBD buildings
SINGAPORE_BUILDING_LOCATIONS: Dict[str, Tuple[float, float]] = {}

for i in range(1, 51):
    bid = f"Building_{i:02d}"  # Building_01, Building_02, ..., Building_50
    # Cycle through CBD buildings (repeat if needed)
    building_idx = (i - 1) % len(CBD_BUILDINGS)
    building_name, lat, lon = CBD_BUILDINGS[building_idx]
    SINGAPORE_BUILDING_LOCATIONS[bid] = (lat, lon)

# Also create a mapping of building IDs to real names for display
BUILDING_NAMES: Dict[str, str] = {}
for i in range(1, 51):
    bid = f"Building_{i:02d}"
    building_idx = (i - 1) % len(CBD_BUILDINGS)
    building_name, _, _ = CBD_BUILDINGS[building_idx]
    BUILDING_NAMES[bid] = building_name
