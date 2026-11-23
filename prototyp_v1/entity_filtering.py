from config import ALLOWED_DOMAINS, EXCLUDED_PREFIXES

# Tato cast kodu sluzi na spajanie dotazov z websocketu, aby sme vedeli ktore zariadenie patri kam.
# Spajanie zariadeni a miestosti funguje cez device_id na zariadenia a area_id na miestnosti.
# V sucasnej dobe obsahuje len veci potrebne pre zariadenia ktore mam vo vm, dalsie doplnim casom.

def _extract_possible_states(state_obj: dict) -> str:
    attrs = state_obj.get("attributes", {})
    domain = state_obj.get("entity_id", "").split(".")[0]

    if "hvac_modes" in attrs:
        return f"Možné hvac módy: {', '.join(attrs['hvac_modes'])}"
    if "options" in attrs:
        return f"Možné stavy: {', '.join(str(o) for o in attrs['options'])}"
    if domain in {"binary_sensor", "light", "switch", "fan"}:
        return "Možné stavy: on, off"
    if domain == "cover":
        return "Možné stavy: open, closed"
    if "unit_of_measurement" in attrs:
        return f"Jednotka: {attrs['unit_of_measurement']}"
    return ""


def filter_and_format_entities(ha_data: dict) -> list[dict]:
    areas = ha_data["areas"]
    devices = ha_data["devices"]
    entity_registry = ha_data["entity_registry"]
    states = ha_data["states"]

    area_map = {area["area_id"]: area["name"] for area in areas}

    device_to_area = {}
    for device in devices:
        dev_id = device["id"]
        area_id = device.get("area_id")
        device_to_area[dev_id] = area_map.get(area_id, "Nezaradené")

    entity_to_device = {
        ent["entity_id"]: ent.get("device_id") for ent in entity_registry
    }

    filtered = []
    for state_obj in states:
        entity_id = state_obj.get("entity_id", "")
        if "." not in entity_id:
            continue

        domain = entity_id.split(".")[0]
        if domain not in ALLOWED_DOMAINS:
            continue

        if any(entity_id.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue

        dev_id = entity_to_device.get(entity_id)
        is_sun_entity = entity_id == "sun.sun" or entity_id.startswith("sensor.sun_")

        if dev_id is None and not is_sun_entity:
            continue

        room = device_to_area.get(dev_id, "Exteriér / Systém (Slnko)" if is_sun_entity else "Nezaradené")
        attrs = state_obj.get("attributes", {})
        friendly_name = attrs.get("friendly_name", entity_id)
        current_state = state_obj.get("state", "unknown")
        possible_info = _extract_possible_states(state_obj)

        parts = [
            f"- {entity_id} ({friendly_name})",
            f"Miestnosť: {room}",
            f"Aktuálny stav: {current_state}",
        ]
        if possible_info:
            parts.append(possible_info)

        filtered.append({
            "entity_id": entity_id,
            "friendly_name": friendly_name,
            "room": room,
            "state": current_state,
            "formatted": " | ".join(parts),
        })

    return sorted(filtered, key=lambda x: x["entity_id"])