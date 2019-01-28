# coding: utf-8
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
class About(object):
    current_datetime: datetime.datetime
    ip: str

    @serpyco.post_dump
    def add_python_version(data: dict) -> dict:
        v = sys.version_info
        data['python_version'] = f"{v.major}.{v.minor}.{v.micro}"
        return data


@dataclass
class EmptyPath(object):
  pass

@hapic.with_api_doc()
@hapic.input_path(EmptyPath)
@hapic.output_body(About)
async def about(request, hapic_data: HapicData):
    return About(
      current_datetime=datetime.datetime.now(),
      ip=get_ip(),
    )


app = web.Application()
app.add_routes([
    web.get(r'/about', about),
])

hapic.set_context(
    AiohttpContext(
        app,
        default_error_builder=SerpycoDefaultErrorBuilder()
    )
)

# FIXME hapic.add_documentation_view('/api-doc', 'DOC', 'Generated doc')
print(json.dumps(hapic.generate_doc()))
aiohttp_autoreload.start()
web.run_app(app)
