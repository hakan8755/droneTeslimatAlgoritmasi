import random, numpy as np
from datetime import time
from typing import List, Tuple
from models import Drone, Delivery, NoFlyZone, Coord

RNG = np.random.default_rng()

def _rand_time(start_h=8, end_h=18) -> Tuple[time, time]:
    t1 = random.randint(start_h, end_h - 2)
    t2 = random.randint(t1 + 1, end_h)
    return time(t1, 0), time(t2, 0)

def generate(
    n_drones=5,
    n_deliveries=20,
    n_zones=2,
    map_size=1000
):
    drones, deliveries, zones = [], [], []
    # Dronelar
    for i in range(n_drones):
        drones.append(
            Drone(
                id=i,
                max_weight=RNG.uniform(1.0, 5.0),
                battery=int(RNG.uniform(8000, 12000)),
                speed=RNG.uniform(12.0, 20.0),
                start_pos=(RNG.uniform(0, map_size), RNG.uniform(0, map_size)),
            )
        )
    # Teslimatlar
    for j in range(n_deliveries):
        deliveries.append(
            Delivery(
                id=j,
                pos=(RNG.uniform(0, map_size), RNG.uniform(0, map_size)),
                weight=RNG.uniform(0.2, 4.5),
                priority=random.randint(1, 5),
                time_window=_rand_time(),
            )
        )
    # No-Fly Zone'lar
    for k in range(n_zones):
        cx, cy = RNG.uniform(0, map_size), RNG.uniform(0, map_size)
        side = RNG.uniform(50, 200)
        coords: List[Coord] = [
            (cx - side, cy - side),
            (cx + side, cy - side),
            (cx + side, cy + side),
            (cx - side, cy + side),
        ]
        zones.append(
            NoFlyZone(
                id=k,
                coordinates=coords,
                active_time=_rand_time(9, 15),
            )
        )
    return drones, deliveries, zones
