import requests
import json
import geopandas as gpd
from shapely.validation import make_valid


class OverpassQuarryExtractor:
    def __init__(self, country):
        self.country = country
        self.geojson_path = f"{self.country}_quarry.geojson"

    def build_query(self):
        return f"""
        [out:json][timeout:60];
        area["ISO3166-1"="{self.country}"][admin_level=2]->.a;
        (
        way["landuse"="quarry"](area.a);
        relation["landuse"="quarry"](area.a);
        way["industrial"="mine"](area.a);
        relation["industrial"="mine"](area.a);
        way["man_made"="tailings_pond"](area.a);
        relation["man_made"="tailings_pond"](area.a);
        );
        out geom;
        """

    def extract_raw(self):
        query = self.build_query()
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data={"data": query}, timeout=60)
        response.raise_for_status()
        return response.json()

    def to_geojson(self, data):
        features = []
        for el in data["elements"]:
            if "geometry" not in el or el["type"] != "way":
                continue
            coords = [(pt["lon"], pt["lat"]) for pt in el["geometry"]]
            if len(coords) < 4:
                continue
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            geometry = {"type": "Polygon", "coordinates": [coords]}
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": el.get("tags", {})
            }
            features.append(feature)
        return {"type": "FeatureCollection", "features": features}

    def save_geojson(self, geojson):
        with open(self.geojson_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f)

    def load_to_geodataframe(self):
        gdf = gpd.read_file(self.geojson_path)
        gdf["geometry"] = gdf["geometry"].apply(
            lambda geom: make_valid(geom) if not geom.is_valid else geom
        )
        gdf = gdf[gdf.geometry.notnull()]
        gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
        return gdf

    def run(self):
        print(f"📡 Extraindo dados para {self.country}...")
        raw = self.extract_raw()
        geojson = self.to_geojson(raw)
        self.save_geojson(geojson)
        gdf = self.load_to_geodataframe()
        print(f"✅ {len(gdf)} pedreiras carregadas.")
        return gdf
