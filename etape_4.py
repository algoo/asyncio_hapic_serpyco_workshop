# coding: utf-8
import datetime
import json
import sys
import typing
from dataclasses import dataclass

from aiohttp import web
from hapic import Hapic, HapicData
from hapic.error.serpyco import SerpycoDefaultErrorBuilder
from hapic.ext.aiohttp.context import AiohttpContext
from hapic.processor.serpyco import SerpycoProcessor
import serpyco


hapic = Hapic(async_=True)
hapic.set_processor_class(SerpycoProcessor)

# This list will contains all client websockets
client_websockets: typing.List[web.WebSocketResponse] = []


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
class Sensor:
    name: str
    location: Location = None


@dataclass
class About(object):
    current_datetime: datetime.datetime
    ip: str

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


sensor_serializer = serpyco.Serializer(Sensor)


async def GET_establish_new_connection(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client_websockets.append(ws)

    async for msg in ws:
        print(f"Message received fom client: {msg.data}")
        await ws.send_str(f'Response of "{msg.data}"')

    print("Websocket connection closed")
    return ws


@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.input_body(SensorName)
@hapic.output_body(Sensor)
async def PUT_sensor_name(request, hapic_data: HapicData):
    print(hapic_data.body)
    sensor.name = hapic_data.body.name

    serialized_sensor = sensor_serializer.dump(sensor)
    for client_websocket in client_websockets:
        await client_websocket.send_json(
            {"type": "NAME_CHANGED", "value": serialized_sensor}
        )

    return sensor


@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.input_body(Location)
@hapic.output_body(Sensor)
async def PUT_sensor_location(request, hapic_data: HapicData):
    print(hapic_data.body)
    sensor.location = Location(lat=hapic_data.body.lat, lon=hapic_data.body.lon)

    serialized_sensor = sensor_serializer.dump(sensor)
    for client_websocket in client_websockets:
        await client_websocket.send_json(
            {"type": "LOCATION_CHANGED", "value": serialized_sensor}
        )

    return sensor


app = web.Application()
app.add_routes(
    [
        web.get("/ws", GET_establish_new_connection),
        web.put(r"/sensor/name", PUT_sensor_name),
        web.put(r"/sensor/location", PUT_sensor_location),
    ]
)

hapic.set_context(
    AiohttpContext(app, default_error_builder=SerpycoDefaultErrorBuilder())
)

hapic.add_documentation_view("/api/doc", "DOC", "Generated doc")
print(json.dumps(hapic.generate_doc()))

web.run_app(app)
