import json
import jsonschema
from jsonschema import validate

def validateJson(jsonData):
    try:
        validate(instance=jsonData, schema=json_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    return True

json_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "price": {"type": "string"},
    "url": {"type": "string"},
    "zone": {"type": "string"},
    "adid": {"type": "string"},
    "UserName": {"type": "string"},
    "ConstructedArea":{"type": "integer"},
    "NumberBathrooms": {"type": "string"},
    "AreaInMeters": {"type": "integer"},
    "Phone": {"type": "string"},
    "ForRentBy": {"type": "string"},
    "WebSiteUrl": {"type": "string"},
    "NumberBedrooms": {"type": "string"},
    "AmenitiesRental": {"type": "string"},
  }
}

jsonobj = {
        "title": "SUITES PARA EJECUTIVOS EN ANZURES PARA ESTRENAR A 2 CALLES TORRE MAYOR Y REFORMA COM MANTENIMIENTO",
        "price": "$18,000 MXN",
        "url": "/a-departamentos-en-renta/anzures/suites-para-ejecutivos-en-anzures-para-estrenar-a-2-calles-torre-mayor-y-reforma-com-mantenimiento/1003810375540911145130209",
        "zone": "Anzures",
        "adid": "1003810375540911145130209",
        "UserName": "Carlos Gonz\u00e1lez Vargas",
        "Parking": 0,
        "DwellingTypeGroup": "Condominios",
        "NumberHalfBathrooms": "2",
        "NumberBathrooms": "1",
        "AreaInMeters": 59,
        "Phone": "(55)7005-5940",
        "ForRentBy": "Agencia",
    }

jsonData = json.loads(json.dumps(jsonobj))
# validate it
isValid = validateJson(jsonobj)
if isValid:
    print(jsonData)
    print("valid")
else:
    print(jsonData)
    print("NOT valid")
