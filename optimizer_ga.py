import random, math
from typing import List, Dict, Tuple, Optional
from itertools import accumulate

from models import Drone, Delivery
from graph_utils import build_graph, edge_cost, euclid, crosses_nfz
import networkx as nx

# ---------- Yardımcı: rota maliyeti (sıralı çok nokta) ---------- #
def route_cost(
    seq: List[Delivery],
    start_pos: Tuple[float, float],
    drone: Drone,
    G: nx.Graph,
    zones,
    mah_per_meter: float = 1.0,
    nfz_penalty: float = 5000.0,
) -> Tuple[float, float]:
    """
    Verilen rota için toplam mesafe ve batarya ihtiyacı.
    Eğer rota bir NFZ'yi keserse ek ceza uygulanır.
    """
    if not seq:
        return 0.0, 0.0

    total_dist, total_cost = 0.0, 0.0
    cur = start_pos

    for dlv in seq:
        goal_pos = dlv.pos
        dist = euclid(cur, goal_pos)
        cost = edge_cost(dist, dlv.weight, dlv.priority)

        # ❗ NFZ ihlali varsa ceza uygula
        if crosses_nfz(cur, goal_pos, zones):
            cost += nfz_penalty

        total_dist += dist
        total_cost += cost
        cur = goal_pos

    # Depoya dönüş
    back = euclid(cur, start_pos)
    if crosses_nfz(cur, start_pos, zones):
        total_cost += nfz_penalty
    total_dist += back
    total_cost += edge_cost(back, 0.0, 1)

    battery_need = total_dist * mah_per_meter
    return total_cost, battery_need

# ---------- Birey kodlaması ---------- #
def decode(
    genome: List[int],
    drones: List[Drone],
    deliveries: List[Delivery],
) -> Dict[int, List[Delivery]]:
    """
    Teslimat permütasyonunu sırayla drone'lara bölerek atama yapar.
    """
    k = len(drones)
    split = math.ceil(len(genome) / k)
    assignment = {d.id: [] for d in drones}
    idx = 0
    for d in drones:
        for _ in range(split):
            if idx < len(genome):
                assignment[d.id].append(deliveries[genome[idx]])
                idx += 1
    return assignment

# ---------- Fitness ---------- #
def fitness(
    genome: List[int],
    drones: List[Drone],
    deliveries: List[Delivery],
    G: nx.Graph,
    zones,
    penalty_big=10000.0,
) -> float:
    """Toplam maliyet + batarya yetmezse büyük ceza + NFZ geçiş cezası"""
    assign = decode(genome, drones, deliveries)
    total = 0.0
    for d in drones:
        seq = assign[d.id]
        cost, mah = route_cost(seq, d.start_pos, d, G, zones)
        if mah > d.battery:
            cost += penalty_big
        total += cost
    return total

# ---------- GA ---------- #
def run_ga(
    drones: List[Drone],
    deliveries: List[Delivery],
    zones,
    pop_size=40,
    generations=150,
    cx_pb=0.8,
    mut_pb=0.2,
) -> Dict:
    G = build_graph(drones, deliveries, zones)
    n = len(deliveries)

    # Başlangıç popülasyonu
    population = [random.sample(range(n), n) for _ in range(pop_size)]
    best_genome, best_score = None, float("inf")

    for gen in range(generations):
        scores = [fitness(g, drones, deliveries, G, zones) for g in population]

        # Elit birey
        elite_idx = scores.index(min(scores))
        if scores[elite_idx] < best_score:
            best_score = scores[elite_idx]
            best_genome = population[elite_idx][:]

        # Yeni popülasyon (elit + turnuva)
        new_pop = [population[elite_idx]]
        while len(new_pop) < pop_size:
            g1, g2 = random.sample(population, 2)
            w1 = fitness(g1, drones, deliveries, G, zones)
            w2 = fitness(g2, drones, deliveries, G, zones)
            parent = g1 if w1 < w2 else g2
            child = parent[:]

            # Çaprazlama (sıraya duyarlı)
            if random.random() < cx_pb:
                other = random.choice(population)
                a, b = sorted(random.sample(range(n), 2))
                seg = other[a:b]
                child = [g for g in child if g not in seg]
                child[a:a] = seg

            # Mutasyon (swap)
            if random.random() < mut_pb:
                i, j = random.sample(range(n), 2)
                child[i], child[j] = child[j], child[i]

            new_pop.append(child)

        population = new_pop

    # En iyi çözümün çıktısı
    best_assign = decode(best_genome, drones, deliveries)
    result = {"score": best_score, "assign": {}}
    for d in drones:
        seq = best_assign[d.id]
        cost, mah = route_cost(seq, d.start_pos, d, G, zones)
        result["assign"][d.id] = {
            "delivery_ids": [dlv.id for dlv in seq],
            "cost": round(cost, 1),
            "battery": f"{int(mah)}/{d.battery}",
        }

    return result
