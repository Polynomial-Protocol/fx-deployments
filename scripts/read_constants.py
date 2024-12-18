import tomli


def read_constants():
    with open("./scripts/constants.toml", "rb") as f:
        return tomli.load(f)
