#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Dict, Generator
import time
from datetime import datetime
import json

from . import Scraper
from . import functions

from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import Source
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)

class SourceVivanuncios(Source):

    def __init__(self) -> None:
        super().__init__()
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0"}
        self.agents_phones = {}

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []

        stream_name = "Properties"

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
          },
          "required": [
            "title",
            "price",
            "url",
            "zone",
            "adid"
          ]
        }

        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema))
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:

        #Get the filters
        url = config["Url"]
        msg = config["Message"]

        variables = {
            "phone": config["Telefono"],
            "site":  config["Sitio"],
            "reference": config["Referencia"]
        }

        #Scrape the data
        start_time = time.time()
        props = Scraper.get_properties(url)
        print(len(props), "Properties extracted in ", time.time()-start_time, " seconds")

        #Send the messages
        print("Start to send messages")
        senders = functions.read_senders()
        Scraper.send_messages(props, senders, variables, msg)
        print("All messages has been sended")

        #Print the messages
        airbyte_messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(stream="Properties", data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
            )
            for data in props
        ]

        yield from airbyte_messages
