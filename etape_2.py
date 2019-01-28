# coding: utf-8
import typing
import json
import socket  # here in order not to avoid
import sys

from dataclasses import dataclass

from aiohttp import web
import aiohttp_autoreload

from hapic import Hapic
from hapic import HapicData
from hapic.error.serpyco import SerpycoDefaultErrorBuilder
from hapic.ext.aiohttp.context import AiohttpContext
from hapic.processor.serpyco import SerpycoProcessor
import serpyco


hapic = Hapic(async_=True)
hapic.set_processor_class(SerpycoProcessor)

import datetime

def get_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
  return s.getsockname()[0]

@dataclass
class Location(object):
  lon: float=serpyco.number_field(cast_on_load=True)
  lat: float=serpyco.number_field(cast_on_load=True)
  #url: typing.Optional[str] = serpyco.string_field(getter="get_openstreetmap_url", init=False)

  def get_openstreetmap_url(data: dict) -> dict:
    data['url'] = f"https://www.openstreetmap.org/search?#map=13/{data['lat']}/{data['lon']}"
    return data

Location(lon=13,lat=24)

@dataclass
class Sensor:
  name: str
  # location: typing.Optional[Location] = None
  location: Location = None

@dataclass
class About(object):
    current_datetime: datetime.datetime
    ip: str

    @serpyco.post_dump
    def add_python_version(data: dict) -> dict:
        v = sys.version_info
        data['python_version'] = f"{v.major}.{v.minor}.{v.micro}"
        return data

sensor = Sensor(name="<no name>", location=Location(lon=19,lat=32))

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
    return About(
      current_datetime=datetime.datetime.now(),
      ip=get_ip(),
    )

@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.input_body(SensorName)
@hapic.output_body(Sensor)
async def PUT_sensor_name(request, hapic_data: HapicData):
  print(hapic_data.body)
  sensor.name = hapic_data.body.name
  return sensor

@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.input_body(Location)
@hapic.output_body(Sensor)
async def PUT_sensor_location(request, hapic_data: HapicData):
  print(hapic_data.body)
  sensor.location = Location(lat=hapic_data.body.lat, lon=hapic_data.body.lon)
  return sensor

app = web.Application()
app.add_routes([
    web.get(r'/about', GET_about),
    web.put(r'/sensor/name', PUT_sensor_name),
    web.put(r'/sensor/location', PUT_sensor_location),
])

hapic.set_context(
    AiohttpContext(
        app,
        default_error_builder=SerpycoDefaultErrorBuilder()
    )
)

hapic.add_documentation_view('/api/doc', 'DOC', 'Generated doc')
print(json.dumps(hapic.generate_doc()))
aiohttp_autoreload.start()
web.run_app(app)
