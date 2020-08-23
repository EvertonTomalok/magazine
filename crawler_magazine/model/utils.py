from schematics import Model


def validate_and_parse_model(data, cls) -> dict:
    model = cls(data)
    model.validate()
    return model.to_primitive()


def validate_model(data, cls) -> Model:
    model = cls(data)
    model.validate()
    return model
