import json
import websocket


class HomeAssistantClient:
    def __init__(self, ws_url: str, token: str):
        self.ws_url = ws_url
        self.token = token

    def _send_ws_command(self, ws, msg_type: str, cmd_id: int):
        ws.send(json.dumps({"id": cmd_id, "type": msg_type}))
        while True:
            response = json.loads(ws.recv())
            if response.get("id") == cmd_id:
                if not response.get("success"):
                    raise RuntimeError(f"HA WS chyba ({msg_type}): {response.get('error')}")
                return response["result"]

    def fetch_environment_data(self) -> dict:
        ws = websocket.create_connection(self.ws_url)
        try:
            auth_req = json.loads(ws.recv())
            if auth_req.get("type") != "auth_required":
                raise RuntimeError(f"Neočakávaná auth správa: {auth_req}")

            ws.send(json.dumps({"type": "auth", "access_token": self.token}))
            auth_response = json.loads(ws.recv())
            if auth_response.get("type") != "auth_ok":
                raise RuntimeError("Autentifikácia do Home Assistantu zlyhala!")

            areas = self._send_ws_command(ws, "config/area_registry/list", 1)
            devices = self._send_ws_command(ws, "config/device_registry/list", 2)
            entity_registry = self._send_ws_command(ws, "config/entity_registry/list", 3)
            states = self._send_ws_command(ws, "get_states", 4)

            return {
                "areas": areas,
                "devices": devices,
                "entity_registry": entity_registry,
                "states": states,
            }
        finally:
            ws.close()