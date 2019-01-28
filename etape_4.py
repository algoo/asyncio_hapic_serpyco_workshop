# coding: utf-8
import asyncio
import datetime
import json
import random
import typing

import aiohttp_autoreload
import serpyco
from aiohttp import web
from hapic import Hapic, HapicData
from hapic.error.serpyco import SerpycoDefaultErrorBuilder
from hapic.ext.aiohttp.context import AiohttpContext
from hapic.processor.serpyco import SerpycoProcessor

from dataclasses import dataclass

import utils

hapic = Hapic(async_=True)
hapic.set_processor_class(SerpycoProcessor)


@dataclass
class Location(object):
    def get_openstreetmap_url(obj: "Location") -> str:
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
    location: Location = None


@dataclass
class About(object):
    current_datetime: datetime.datetime
    ip: str

    @staticmethod
    @serpyco.post_dump
    def add_python_version(data: dict) -> dict:
        data["python_version"] = utils.get_python_version()
        return data


sensor = Sensor(name="<no name>", location=Location(lon=19, lat=32))
sensor_serializer = serpyco.Serializer(Sensor)

# This list will contains all client websockets
client_websockets: typing.List[web.WebSocketResponse] = []


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
    return About(current_datetime=datetime.datetime.now(), ip=utils.get_ip())


@hapic.with_api_doc()
@hapic.output_body(Sensor)
async def GET_sensor(request):
    return sensor


async def update_sensor(partial_sensor: PartialSensor) -> Sensor:
    name_changed = False
    location_changed = False

    if partial_sensor.name and sensor.name != partial_sensor.name:
        sensor.name = partial_sensor.name
        name_changed = True

    if partial_sensor.location:
        if sensor.location != partial_sensor.location:
            sensor.location = partial_sensor.location
            location_changed = True

    # Send changes on websockets
    if name_changed or location_changed:
        serialized_sensor = sensor_serializer.dump(sensor)

        if name_changed:
            for client_websocket in client_websockets:
                await client_websocket.send_json(
                    {"type": "NAME_CHANGED", "value": serialized_sensor}
                )
        if location_changed:
            for client_websocket in client_websockets:
                await client_websocket.send_json(
                    {"type": "LOCATION_CHANGED", "value": serialized_sensor}
                )

    return sensor


@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.input_body(PartialSensor)
@hapic.output_body(Sensor)
async def PATCH_sensor(request, hapic_data: HapicData):
    print(hapic_data.body)
    return await update_sensor(hapic_data.body)


@dataclass
class Measure:
    datetime: datetime.datetime
    temperature: float


@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.output_stream(Measure)
async def GET_sensor_live(request, hapic_data: HapicData):
    while True:
        yield Measure(datetime.datetime.now(), utils.get_temperature())
        await asyncio.sleep(1)


async def GET_establish_new_connection(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client_websockets.append(ws)

    async for msg in ws:
        print(f"Message received fom client: {msg.data}")
        await ws.send_str(f'Response of "{msg.data}"')

    print("Websocket connection closed")
    return ws


app = web.Application()
app.add_routes(
    [
        web.get(r"/about", GET_about),
        web.patch(r"/sensor", PATCH_sensor),
        web.get(r"/sensor", GET_sensor),
        web.get(r"/sensor/live", GET_sensor_live),
        web.get("/sensor/events", GET_establish_new_connection),
    ]
)

hapic.set_context(
    AiohttpContext(app, default_error_builder=SerpycoDefaultErrorBuilder())
)


hapic.add_documentation_view("/api/doc", "DOC", "Generated doc")
print(json.dumps(hapic.generate_doc()))
aiohttp_autoreload.start()
web.run_app(app)
