from schematics.models import Model
from schematics.types import (
    IntType,
    StringType,
    FloatType,
)


class PartialProduct(Model):
    category = StringType(required=True)
    department = StringType(required=True)
    image_url = StringType(required=True)
    marca = StringType(required=True)
    taxa_de_juros = StringType()
    valor_parcela = FloatType()
    parcelas = IntType()
    preco_por = FloatType()
    sub_category = StringType(required=True)
    url = StringType(required=True)
    estoque = StringType(required=True)

    # metadata = DictType(StringType, serialize_when_none=False)
