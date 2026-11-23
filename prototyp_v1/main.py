import json
from config import (
    HA_TOKEN,
    HA_WS_URL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
    SYSTEM_PROMPT_PATH,
    USER_PROMPT_TEMPLATE_PATH,
)
from entity_filtering import filter_and_format_entities
from home_assistant_client import HomeAssistantClient
from ai_client import OllamaClient
from prompt_building import (
    build_system_prompt,
    build_user_prompt,
    build_yaml_user_prompt,
)


def main():
    ha_client = HomeAssistantClient(ws_url=HA_WS_URL, token=HA_TOKEN)
    ollama_client = OllamaClient(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=OLLAMA_TEMPERATURE,
    )

    print("1. Sťahujem a filtrujem entity z Home Assistantu...")
    ha_data = ha_client.fetch_environment_data()
    entities = filter_and_format_entities(ha_data)
    print(f"Načítaných filtrovaných entít: {len(entities)}")

    print("\n--- Vyfiltrované entity, ktoré sa pošlú s promptom ---")
    for ent in entities:
        print(ent["formatted"])
    print("-------------------------------------------------\n")

    # Sem sa dáva request, zatiaľ to bere len takto, do budúcna to zmením
    system_prompt = build_system_prompt(SYSTEM_PROMPT_PATH)
    request = "Vypni klimatizáciu v obývačke, ak sa otvorí okno v obývačke."

    print("\n2. Posielam požiadavku na medzikód (JSON) do Ollamy...")
    user_prompt_json = build_user_prompt(
        template_path=USER_PROMPT_TEMPLATE_PATH,
        entities=entities,
        user_request=request,
        target_structure="[ŠTRUKTÚRA 1: JSON Medzikód]",
    )
    json_output = ollama_client.chat(system_prompt=system_prompt, user_prompt=user_prompt_json)
    print("--- Výstup medzikódu (JSON) ---")
    print(json_output)

    try:
        cleaned = json_output.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        print("\nUpozornenie: Výstup nebol platný JSON, YAML krok preskakujem.")
        return

    if parsed.get("status") == "success":
        print("\n3. Prevádzam JSON medzikód na finálny YAML...")
        user_prompt_yaml = build_yaml_user_prompt(json.dumps(parsed, indent=2, ensure_ascii=False))
        yaml_output = ollama_client.chat(system_prompt=system_prompt, user_prompt=user_prompt_yaml)
        print("--- Výstup finálnej automatizácie (YAML) ---")
        print(yaml_output)
    else:
        print("\nModel vrátil ne-úspešný stav (napr. chybu / upresnenie):", parsed)


if __name__ == "__main__":
    main()