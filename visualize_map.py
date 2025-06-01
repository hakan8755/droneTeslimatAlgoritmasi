import folium
from typing import List, Tuple
from models import Drone, Delivery, NoFlyZone

def project(coord: Tuple[float, float], origin: Tuple[float, float] = (40.76, 29.92)) -> Tuple[float, float]:
    """
    Basit dönüşüm: metre koordinatını enleme-boylama çevirmek için kaba ölçekleme.
    1 derece enlem ≈ 111 km, 1 derece boylam ≈ 85 km (Kocaeli civarı).
    """
    lat = origin[0] + (coord[1] / 111000)  # y → enlem
    lon = origin[1] + (coord[0] / 85000)   # x → boylam
    return lat, lon

def draw_map(
    drones: List[Drone],
    result: dict,
    deliveries: List[Delivery],
    zones: List[NoFlyZone],
    filename: str = "map.html"
):
    m = folium.Map(location=project((500, 500)), zoom_start=14)

    # Teslimatları dict'e çevir
    dlv_dict = {dlv.id: dlv for dlv in deliveries}

    colors = ["red", "blue", "green", "orange", "purple", "black"]

    for i, drone in enumerate(drones):
        info = result["assign"][drone.id]
        dlv_ids = info["delivery_ids"]
        path_coords = [drone.start_pos]

        for dlv_id in dlv_ids:
            path_coords.append(dlv_dict[dlv_id].pos)
        path_coords.append(drone.start_pos)

        # Noktaları çiz
        for j, coord in enumerate(path_coords):
            latlon = project(coord)
            if j == 0:
                folium.Marker(latlon, icon=folium.Icon(color=colors[i % len(colors)], icon="home"),
                              popup=f"Drone {drone.id} Start").add_to(m)
            elif j == len(path_coords) - 1:
                folium.Marker(latlon, icon=folium.Icon(color="gray", icon="arrow-down"),
                              popup=f"Drone {drone.id} Return").add_to(m)
            else:
                folium.CircleMarker(latlon, radius=6, color=colors[i % len(colors)],
                                    fill=True, fill_opacity=0.7,
                                    popup=f"Delivery {dlv_ids[j-1]}").add_to(m)

        # Rota çizgisi
        folium.PolyLine([project(c) for c in path_coords],
                        color=colors[i % len(colors)],
                        weight=3, opacity=0.8,
                        tooltip=f"Drone {drone.id} rotası").add_to(m)

    # No-Fly Zone'ları çiz
    for zone in zones:
        coords = [project(pt) for pt in zone.coordinates]
        coords.append(coords[0])  # poligon kapanmalı

        folium.Polygon(
            locations=coords,
            color='red',
            fill=True,
            fill_opacity=0.3,
            popup=f"NFZ {zone.id} ({zone.active_time[0].strftime('%H:%M')}–{zone.active_time[1].strftime('%H:%M')})"
        ).add_to(m)

    m.save(filename)
    print(f"🗺️ Harita oluşturuldu: {filename}")
