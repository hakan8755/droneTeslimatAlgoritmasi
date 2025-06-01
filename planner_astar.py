# planner_astar.py
import math, heapq, networkx as nx
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple, Optional

from models import Drone, Delivery
from graph_utils import edge_cost, euclid

# -------- Yardımcı: Heuristik -------- #
def _heuristic(n: str, goal: str, pos: Dict[str, Tuple[float, float]]) -> float:
    """A* için öklid mesafe tabanlı sezgi (admissible)."""
    return euclid(pos[n], pos[goal])

# -------- Ana planlayıcı -------- #
def plan_route(
    drone: Drone,
    deliveries: List[Delivery],
    G: nx.Graph,
    cruise_current_mA: float = 15000.0,  # (örnek) 15 A
    mah_per_meter: float = 1.0,          # kaba tahmin
) -> Optional[Dict]:
    """
    • Şimdilik tek teslimat seçip o noktaya gidip geri dönmeyi planlar.  
    • Bataryayı, ağırlığı ve zaman penceresini kontrol eder.
    """
    result = []

    for dlv in deliveries:
        start = f"D{drone.id}"
        goal  = f"L{dlv.id}"

        if not G.has_node(start) or not G.has_node(goal):
            continue

        # A* arama – NetworkX hazır fonksiyon
        try:
            path = nx.astar_path(
                G,
                start,
                goal,
                heuristic=lambda n1, n2=goal: _heuristic(n1, n2, nx.get_node_attributes(G, "pos")),
                weight="distance"
            )
        except nx.NetworkXNoPath:
            continue

        # Maliyet & batarya tüketimi
        total_dist, total_cost = 0.0, 0.0
        for u, v in zip(path[:-1], path[1:]):
            d = G.edges[u, v]["distance"]
            c = edge_cost(d, dlv.weight, dlv.priority)
            total_dist  += d
            total_cost  += c

        # Geri dönüş (basitçe düz hat; NFZ’yi kesiyorsa discard edilir)
        back_dist = euclid(G.nodes[path[-1]]["pos"], G.nodes[start]["pos"])
        if back_dist == math.inf:
            continue
        total_dist += back_dist
        total_cost += edge_cost(back_dist, 0.0, 1)

        # Batarya kontrolü (çok kaba): mAh ≈ mesafe·mah_per_meter
        needed_mah = total_dist * mah_per_meter
        if needed_mah > drone.battery:
            continue

        # Teslimat zaman penceresi (örn. simülasyonda kalkış 09:00 kabul)
        depart = time(9, 0)
        avg_speed = drone.speed                # m/s
        eta_sec   = total_dist / avg_speed
        arrival   = (datetime.combine(datetime.today(), depart) +
                     timedelta(seconds=eta_sec)).time()

        if not (dlv.time_window[0] <= arrival <= dlv.time_window[1]):
            continue

        # Başarılı rota
        result.append({
            "delivery_id": dlv.id,
            "path": path,
            "distance": round(total_dist, 1),
            "cost": round(total_cost, 1),
            "eta": arrival.strftime("%H:%M"),
            "battery_needed": int(needed_mah),
        })

    # En düşük maliyetliyi seç
    if not result:
        return None
    return min(result, key=lambda r: r["cost"])
