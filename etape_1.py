# coding: utf-8
import datetime
import json

import aiohttp_autoreload
import serpyco
from aiohttp import web
from hapic import Hapic
from hapic.error.serpyco import SerpycoDefaultErrorBuilder
from hapic.ext.aiohttp.context import AiohttpContext
from hapic.processor.serpyco import SerpycoProcessor

import utils
from dataclasses import dataclass

hapic = Hapic(async_=True)
hapic.set_processor_class(SerpycoProcessor)


@dataclass
class About(object):
    current_datetime: datetime.datetime
    ip: str

    @staticmethod
    @serpyco.post_dump
    def add_python_version(data: dict) -> dict:
        data["python_version"] = utils.get_python_version()
        return data


@hapic.with_api_doc()
@hapic.output_body(About)
async def about(request):
    return About(current_datetime=datetime.datetime.now(), ip=utils.get_ip())


app = web.Application()
app.add_routes([web.get(r"/about", about)])

hapic.set_context(
    AiohttpContext(app, default_error_builder=SerpycoDefaultErrorBuilder())
)

hapic.add_documentation_view("/api/doc", "DOC", "Generated doc")
print(json.dumps(hapic.generate_doc()))
aiohttp_autoreload.start()
web.run_app(app)
