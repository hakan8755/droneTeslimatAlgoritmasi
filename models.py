from dataclasses import dataclass
from datetime import time
from typing import Tuple, List

Coord = Tuple[float, float]          # (x, y) metre

@dataclass
class Drone:
    id: int
    max_weight: float                # kg
    battery: int                     # mAh
    speed: float                     # m/s
    start_pos: Coord

@dataclass
class Delivery:
    id: int
    pos: Coord
    weight: float                    # kg
    priority: int                    # 1–5
    time_window: Tuple[time, time]   # (start, end)

@dataclass
class NoFlyZone:
    id: int
    coordinates: List[Coord]         # poligon köşeleri
    active_time: Tuple[time, time]   # (start, end)
