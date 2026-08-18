from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import urllib.request


GEOJSON_URL = "https://raw.githubusercontent.com/gilmarcarmojr-blip/processos-geojson/refs/heads/main/teste.geojson"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:
            # Lê os parâmetros da URL
            query = parse_qs(urlparse(self.path).query)

            ordens = query.get("ordem", [])

            # Baixa o GeoJSON completo
            with urllib.request.urlopen(GEOJSON_URL) as response:
                data = json.loads(response.read().decode("utf-8"))

            # Se não houver filtro, retorna tudo
            if not ordens:
                resultado = data

            else:
                # Converte "1,2,31" em uma lista
                lista_ordens = []

                for item in ordens:
                    lista_ordens.extend(
                        [x.strip() for x in item.split(",") if x.strip()]
                    )

                # Filtra os polígonos pela propriedade ORDEM
                features = []

                for feature in data.get("features", []):

                    ordem = feature.get("properties", {}).get("ORDEM")

                    if str(ordem) in lista_ordens:
                        features.append(feature)

                resultado = {
                    "type": "FeatureCollection",
                    "features": features
                }

            # Resposta
            corpo = json.dumps(resultado).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/geo+json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()

            self.wfile.write(corpo)

        except Exception as e:

            erro = json.dumps({
                "erro": str(e)
            }).encode("utf-8")

            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(erro)
