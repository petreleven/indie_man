from typing import Dict
from quart import Quart, render_template, request
from sqlalchemy import True_
from sqlalchemy.orm import context
from blueprints.api.workers_endpoints import api_workers
import os
from DataAccessLayer.models import Base
from DataAccessLayer.db_connection_layer import engine, local_data_access

app = Quart(__name__)
app.register_blueprint(api_workers)
# set template and static folder
template_folder = os.path.join(os.path.dirname(__file__), "templates/")
static_folder = os.path.join(os.path.dirname(__file__), "static/")
app.template_folder = template_folder
app.static_folder = static_folder


# Ensure db exists before startup
@app.before_serving
async def create_db_tables():
    return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def index():
    return await render_template(
        template_name_or_list="index.html",
        context={
            "topTableOverviews": [1, 2, 3],
            "bottomTableOverviews": [1, 2, 3],
        },
    )


@app.route("/channels/all",methods =["GET", "POST"])
async def channel_genres():
    data = {}
    async with local_data_access() as _streamer_dal:
       data = await _streamer_dal.get_all_streamers_paginated(page_number=1)
    return await render_template(
        template_name_or_list="channels.html",
        context=data,
    )


@app.route("/exp",methods =["GET", "POST"])
async def exp():
    print(await request.body)
    return await render_template(
        template_name_or_list="exp.html",
    )

@app.get("/all")
async def all():
    async with local_data_access() as _streamer_dal:
        data = await _streamer_dal.get_all_streamers()
    return data


@app.get("/view_streamer")
async def view_streamer():
    return await render_template(template_name_or_list="streamer.html", context={})


@app.post("/create_streamer/")
async def create_streamer():
    data = await request.get_json()
    print(data)
    async with local_data_access() as _streamer_dal:
        await _streamer_dal.create_stremer(data)
    return "operation finished"

import time
@app.post("/filter_streamers")
async def filter_streamers():
    # assuming genre="indie"&genre="something"&platform="yt"..etc
    req_filters = await request.body

    req_filters = req_filters.decode('utf-8')
    sanitized_filters = {"genres": [], "platforms": []}
    _split_helper(req_filters, sanitized_filters)
    print("sanitized_filters: ", sanitized_filters)
    async with local_data_access() as _streamer_dal:
        db_or_redis_response = await _streamer_dal.filter_streamers_by_genre(
            sanitized_filters
        )
    print(db_or_redis_response)
    return await render_template(template_name_or_list="channels_partials.html",
                           context=db_or_redis_response)


def _split_helper(req_filters: str, sanitized_filters: Dict[str, list]):
    filters = req_filters.split("&")
    for x in filters:
        arr = x.split("=")
        if arr[0] == "genre":
            sanitized_filters["genres"].append(arr[1])
            continue
        if arr[0] =="platforms":
            sanitized_filters["platforms"].append(arr[1])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)
