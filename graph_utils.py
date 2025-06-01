# graph_utils.py
import math
import networkx as nx
from shapely.geometry import LineString, Polygon, Point
from typing import List

from models import Drone, Delivery, NoFlyZone, Coord

# ---------- Yardımcı hesaplamalar ---------- #
def euclid(a: Coord, b: Coord) -> float:
    """İki noktayı metre cinsinden Öklid uzaklığı."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def crosses_nfz(p1: Coord, p2: Coord, zones: List[NoFlyZone]) -> bool:
    """p1‒p2 doğrusu herhangi bir NFZ poligonunu kesiyorsa True döner."""
    seg = LineString([p1, p2])
    for z in zones:
        poly = Polygon(z.coordinates)
        if seg.crosses(poly):
            return True
    return False

# ---------- Graf oluşturma ---------- #
def build_graph(
    drones: List[Drone],
    deliveries: List[Delivery],
    zones: List[NoFlyZone],
) -> nx.Graph:
    """
    • Droneların başlangıç noktaları + bütün teslimat adresleri düğüm.  
    • Kenarlar iki düğüm arasında NFZ kesmiyorsa eklenir.  
    • Ağırlık = mesafe (metre).
    """
    G = nx.Graph()

    # Düğüm listesi (id prefix ile çakışma önlenir)
    for d in drones:
        G.add_node(f"D{d.id}", pos=d.start_pos, typ="drone")
    for dlv in deliveries:
        G.add_node(f"L{dlv.id}", pos=dlv.pos, typ="delivery")

    # Tüm çiftler (tam grafa yakın; büyük projelerde K-d tree ile inceltilebilir)
    nodes = list(G.nodes(data=True))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            id1, data1 = nodes[i]
            id2, data2 = nodes[j]
            p1, p2 = data1["pos"], data2["pos"]

            # NFZ kesiyorsa kenar ekleme
            if crosses_nfz(p1, p2, zones):
                continue

            dist = euclid(p1, p2)
            G.add_edge(id1, id2, distance=dist)

    return G

# ---------- Maliyet fonksiyonu ---------- #
def edge_cost(distance: float, payload_kg: float, priority: int) -> float:
    """
    • distance : metre  
    • payload  : kg  
    • priority : 1 (düşük) … 5 (acil)  
    Basit örnek → maliyet = mesafe + 50 · kg + 200 · (priority – 1)
    """
    return distance + 50 * payload_kg + 200 * (priority - 1)
