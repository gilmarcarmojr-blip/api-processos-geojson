from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import urllib.request
import re

GEOJSON_URL = "https://raw.githubusercontent.com/gilmarcarmojr-blip/processos-geojson/refs/heads/main/teste.geojson"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            caminho = urlparse(self.path).path

            # Aceita:
            # /api/processo/31
            # /api/processo/31,32
            match = re.search(r"/api/processo/(.+)$", caminho)

            if not match:
                self.enviar_erro(404, "Ordem não informada")
                return

            ordens = match.group(1).split(",")

            ordens = [
                ordem.strip()
                for ordem in ordens
                if ordem.strip()
            ]

            # Carrega GeoJSON original
            with urllib.request.urlopen(
                GEOJSON_URL,
                timeout=20
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            # Filtra
            features = [
                feature
                for feature in data.get("features", [])
                if str(
                    feature.get("properties", {}).get("ORDEM")
                ) in ordens
            ]

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
            self.enviar_erro(500, str(e))

    def enviar_erro(self, codigo, mensagem):

        corpo = json.dumps({
            "erro": mensagem
        }).encode("utf-8")

        self.send_response(codigo)

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
