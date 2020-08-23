from schematics.models import Model
from schematics.types import (
    IntType,
    StringType,
    FloatType, DictType,
)


class PartialProduct(Model):
    categoria = StringType(required=True)
    sub_categoria = StringType(required=True)
    departmento = StringType(required=True)
    image_url = StringType(required=True)
    marca = StringType(required=True)
    taxa_de_juros = StringType()
    valor_parcela = FloatType()
    parcelas = IntType()
    preco_por = FloatType()
    url = StringType(required=True)
    estoque = StringType(required=True)


class DetailProduct(Model):
    produto = StringType(required=True)
    ean = StringType(required=True)
    sku = StringType(required=True)
    atributos = DictType(StringType, serialize_when_none=False)


class Product(Model):
    categoria = StringType(required=True)
    sub_categoria = StringType(required=True)
    departmento = StringType(required=True)
    image_url = StringType(required=True)
    marca = StringType(required=True)
    taxa_de_juros = StringType()
    valor_parcela = FloatType()
    parcelas = IntType()
    preco_por = FloatType()
    url = StringType(required=True)
    estoque = StringType(required=True)
    produto = StringType(required=True)
    ean = StringType(required=True)
    sku = StringType(required=True)
    atributos = DictType(StringType, serialize_when_none=False)
    metadata = DictType(StringType, serialize_when_none=False)
