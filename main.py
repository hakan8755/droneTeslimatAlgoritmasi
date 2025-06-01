from data_generator import generate
from graph_utils import build_graph
from planner_astar import plan_route
from optimizer_ga import run_ga
from visualize_map import draw_map

# Veri üretimi
drones, deliveries, zones = generate(n_drones=5, n_deliveries=25, n_zones=3)
G = build_graph(drones, deliveries, zones)

print(f"Graf → {G.number_of_nodes()} düğüm, {G.number_of_edges()} kenar\n")

# === A* Testi – İlk drone için en iyi tekli teslimat ===
print("=== A* (tekli teslimat) testi ===")
route = plan_route(drones[0], deliveries, G)
if route:
    print(f"🚁 Drone {drones[0].id} ► Teslimat {route['delivery_id']}")
    print(f"  Yol       : {' ➜ '.join(route['path'])}")
    print(f"  Mesafe    : {route['distance']} m")
    print(f"  Maliyet   : {route['cost']}")
    print(f"  ETA       : {route['eta']}")
    print(f"  Batarya   : {route['battery_needed']} / {drones[0].battery} mAh\n")
else:
    print("Uygun teslimat bulunamadı.\n")

# === GA Testi – Çoklu drone ve çoklu teslimat optimizasyonu ===
print("=== Genetik Algoritma testi ===")
result = run_ga(
    drones,
    deliveries,
    zones,
    pop_size=40,
    generations=150
)

print(f"\n✅ GA Sonuç: Toplam skor = {result['score']:.1f}\n")
for d in drones:
    info = result["assign"][d.id]
    print(f"🚁 Drone {d.id} teslimatlar: {info['delivery_ids']}")
    print(f"   maliyet={info['cost']}  batarya={info['battery']}\n")

draw_map(drones, result, deliveries, zones, filename="drone_routes.html")