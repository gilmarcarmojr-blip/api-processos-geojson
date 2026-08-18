from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import json
import urllib.request
import re

GEOJSON_URL = "https://raw.githubusercontent.com/gilmarcarmojr-blip/processos-geojson/refs/heads/main/teste.geojson"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            lista_ordens = []

            # -------------------------------------------------
            # 1. Tenta pegar as ordens pelo parâmetro ?ordem=
            # -------------------------------------------------
            ordens_param = query.get("ordem", [])

            for valor in ordens_param:
                for item in valor.split(","):
                    item = item.strip()

                    if item:
                        lista_ordens.append(item)

            # -------------------------------------------------
            # 2. Se não encontrou ?ordem=,
            #    tenta pegar pelo caminho:
            #
            # /api/processo/31.geojson
            # /api/processo/31,32.geojson
            # -------------------------------------------------
            if not lista_ordens:

                caminho = unquote(parsed.path)

                match = re.search(
                    r"/processo/([^/]+)\.geojson$",
                    caminho
                )

                if match:

                    ordens_caminho = match.group(1)

                    for item in ordens_caminho.split(","):
                        item = item.strip()

                        if item:
                            lista_ordens.append(item)

            # -------------------------------------------------
            # 3. Carrega o GeoJSON original
            # -------------------------------------------------
            with urllib.request.urlopen(
                GEOJSON_URL,
                timeout=20
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            # -------------------------------------------------
            # 4. Filtra as ordens
            # -------------------------------------------------
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

            # -------------------------------------------------
            # 5. Monta o FeatureCollection
            # -------------------------------------------------
            resultado = {
                "type": "FeatureCollection",
                "features": features
            }

            corpo = json.dumps(
                resultado,
                ensure_ascii=False
            ).encode("utf-8")

            # -------------------------------------------------
            # 6. Resposta
            # -------------------------------------------------
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

            self.send_header(
                "Cache-Control",
                "no-cache"
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
