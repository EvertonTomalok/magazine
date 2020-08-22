
def validate_and_parse_model(data, cls):
    model = cls(data)
    model.validate()
    return model.to_primitive()


def validate_model(data, cls):
    model = cls(data)
    model.validate()
    return model
