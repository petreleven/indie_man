from typing import Dict, List
from quart import(
    Quart,
    render_template,
    request
)

import os
from DataAccessLayer.models import Base
from DataAccessLayer.db_connection_layer import engine, local_data_access
app = Quart(__name__)
# set template and static folder
template_folder = os.path.join(os.getcwd(), "templates/")
static_folder = os.path.join(os.getcwd(), "static/")
app.template_folder = template_folder
app.static_folder = static_folder


#Ensure db exists before startup
@app.before_serving
async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def index():
    return await render_template(
        template_name_or_list="index.html",
        context={"topTableOverviews": [1, 2, 3], "bottomTableOverviews": [1, 2, 3]},
    )


@app.get("/channels/<string:genres>")
async def channel_genres(genres):
    return await render_template(
        template_name_or_list="channels.html",
        context={"channels": [i for i in range(30)]},
    )

@app.post("/create_streamer/")
async def create_streamer():
    data = await request.get_json()
    print(data)
    async with local_data_access() as _streamer_dal:
        await _streamer_dal.create_stremer(data)
    return "operation finished"

@app.get("/filter_by_genre/<string:req_filters>")
async def filter_by_genre(req_filters : str):
    #assuming genre="indie"&genre="something"&platform="yt"..etc
    print("*"*20)
    print("raw ",req_filters)
    sanitized_filters = {"genres":[],
                         "platforms":[]}
    _split_helper(req_filters, sanitized_filters)
    print("sanitized_filters: ",sanitized_filters)
    async with local_data_access() as _streamer_dal:
        db_or_redis_response = await _streamer_dal.filter_streamers_by_genre(sanitized_filters)
    print("db/redis:", db_or_redis_response)
    return "done"

def _split_helper(req_filters : str, sanitized_filters : Dict[str, list]):
    filters = req_filters.split("&")
    for x in filters:
        arr = x.split("=")
        if arr[0]=="genre":
            sanitized_filters["genres"].append(arr[1])
            continue
        sanitized_filters["platforms"].append(arr[1])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)
