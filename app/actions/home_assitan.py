import requests

HOME_ASSISTANT_URL = "http://localhost:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlYjg3ZjZmMTZlMDc0NzA3YmRiOWQzZjU5MThmYzQ3MCIsImlhdCI6MTc3ODU1MTQ2OCwiZXhwIjoyMDkzOTExNDY4fQ.OSz40lYqzsAxQ1Y-E81EKqPVN8GfVoCUejL_DjMTHMs"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Encender una luz
def encender_luz(entity_id):
    requests.post(
        f"{HOME_ASSISTANT_URL}/api/services/light/turn_on",
        headers=headers,
        json={"entity_id": entity_id}
    )

# Apagar cualquier dispositivo
def apagar_dispositivo(entity_id):
    requests.post(
        f"{HOME_ASSISTANT_URL}/api/services/homeassistant/turn_off",
        headers=headers,
        json={"entity_id": entity_id}
    )