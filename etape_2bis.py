# coding: utf-8
import asyncio
import datetime
import json
import socket  # here in order not to avoid
import sys
import typing

import aiohttp_autoreload
import serpyco
from aiohttp import web
from hapic import Hapic, HapicData
from hapic.error.serpyco import SerpycoDefaultErrorBuilder
from hapic.ext.aiohttp.context import AiohttpContext
from hapic.processor.serpyco import SerpycoProcessor

from dataclasses import dataclass

hapic = Hapic(async_=True)
hapic.set_processor_class(SerpycoProcessor)



def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
    return s.getsockname()[0]


@dataclass
class Location(object):
    def get_openstreetmap_url(obj: "Location") -> dict:
        return f"https://www.openstreetmap.org/search?#map=13/{obj.lat}/{obj.lon}"

    lon: float = serpyco.number_field(cast_on_load=True)
    lat: float = serpyco.number_field(cast_on_load=True)
    url: typing.Optional[str] = serpyco.string_field(
        getter=get_openstreetmap_url, default=None
    )


@dataclass
class PartialSensor:
    name: typing.Optional[str] = ""
    location: typing.Optional[Location] = None


@dataclass
class Sensor:
    name: str
    # location: typing.Optional[Location] = None
    location: Location = None


@dataclass
class About(object):
    current_datetime: datetime.datetime
    ip: str

    @staticmethod
    @serpyco.post_dump
    def add_python_version(data: dict) -> dict:
        v = sys.version_info
        data["python_version"] = f"{v.major}.{v.minor}.{v.micro}"
        return data


sensor = Sensor(name="<no name>", location=Location(lon=19, lat=32))


@dataclass
class EmptyPath(object):
    pass


@dataclass
class SensorName:
    name: str


@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.output_body(About)
async def GET_about(request, hapic_data: HapicData):
    return About(current_datetime=datetime.datetime.now(), ip=get_ip())


@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.input_body(PartialSensor)
@hapic.output_body(Sensor)
async def PATCH_sensor(request, hapic_data: HapicData):
    print(hapic_data.body)
    if hapic_data.body.name and sensor.name != hapic_data.body.name:
        sensor.name = hapic_data.body.name

    if hapic_data.body.location:
        if sensor.location != hapic_data.body.location:
            sensor.location = hapic_data.body.location

    return sensor


app = web.Application()
app.add_routes([web.get(r"/about", GET_about), web.patch(r"/sensor", PATCH_sensor)])

hapic.set_context(
    AiohttpContext(app, default_error_builder=SerpycoDefaultErrorBuilder())
)


hapic.add_documentation_view("/api/doc", "DOC", "Generated doc")
print(json.dumps(hapic.generate_doc()))
aiohttp_autoreload.start()
web.run_app(app)
