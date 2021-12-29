def read_help_text(file_name: str) -> str:
    with open(f"help_texts/{file_name}", "r", encoding="utf-8") as f:
        return f.read()
