def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_system_prompt(system_prompt_path: str) -> str:
    return load_text_file(system_prompt_path)


def build_user_prompt(
    template_path: str,
    entities: list[dict],
    user_request: str,
    target_structure: str = "[ŠTRUKTÚRA 1: JSON Medzikód]",
) -> str:
    template = load_text_file(template_path)
    entities_block = "\n".join(item["formatted"] for item in entities)
    return template.format(
        entities_block=entities_block,
        user_request=user_request,
        target_structure=target_structure,
    )


def build_yaml_user_prompt(json_middleware_code: str) -> str:
    return (
        f"[Dostupný JSON medzikód]\n{json_middleware_code}\n\n"
        "[Pokyn]\n"
        "Na základe dodaného JSON medzikódu vygeneruj hotovú Home Assistant "
        "automatizáciu v štruktúre [ŠTRUKTÚRA 2: Finálny YAML]."
    )