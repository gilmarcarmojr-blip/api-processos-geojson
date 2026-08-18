from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import urllib.request


GEOJSON_URL = "https://raw.githubusercontent.com/gilmarcarmojr-blip/processos-geojson/refs/heads/main/teste.geojson"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:

            # Lê os parâmetros da URL
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            # Exemplo:
            # ?ordem=31
            # ?ordem=31,32

            ordens_param = query.get("ordem", [])

            lista_ordens = []

            for valor in ordens_param:
                for item in valor.split(","):
                    item = item.strip()

                    if item:
                        lista_ordens.append(item)

            # Carrega o GeoJSON
            with urllib.request.urlopen(
                GEOJSON_URL,
                timeout=20
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            # Filtra pelas ordens
            if lista_ordens:

                features = [
                    feature
                    for feature in data.get("features", [])
                    if str(
                        feature.get("properties", {}).get("ORDEM")
                    ) in lista_ordens
                ]

            else:

                features = data.get("features", [])

            resultado = {
                "type": "FeatureCollection",
                "features": features
            }

            corpo = json.dumps(
                resultado,
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/geo+json"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.send_header(
                "Content-Disposition",
                "inline"
            )

            self.end_headers()

            self.wfile.write(corpo)

        except Exception as e:

            corpo = json.dumps({
                "erro": str(e)
            }).encode("utf-8")

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            self.wfile.write(corpo)
