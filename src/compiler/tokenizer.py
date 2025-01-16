import re
def tokenize(source_code: str) -> list[str]:
    model = re.compile(r'([A-Za-z_][A-Za-z0-9_]*|[0-9]+)')
    return model.findall(source_code)