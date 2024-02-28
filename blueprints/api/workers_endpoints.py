from quart import Blueprint, request
from DataAccessLayer.db_connection_layer import local_data_access

api_workers = Blueprint("api_workers", __name__)


@api_workers.get("/api/get_streamer")
async def api_get_streamer():
    data = await request.get_json()
    print(data)
    exists = False
    async with local_data_access() as _streamer_dal:
        exists = await _streamer_dal.api_get_streamer(data)
    print("dooooone")
    return {"exists": exists}


@api_workers.get("/api/api_get_streamer_paginated")
async def api_get_streamer_paginated():
    async with local_data_access() as _streamer_dal:
        data = await _streamer_dal.api_get_all_streamers_paginated()
    return data


@api_workers.post("/api/update_streamer_videos/")
async def api_update_streamer_videos():
    data = await request.get_json()
    print(data)
    async with local_data_access() as _streamer_dal:
        await _streamer_dal.add_video_history_streamer(data["id"], data["videos"])
    return "done"       


@api_workers.route("/api/update_streamer_genres/", methods =["GET", "POST"])
async def api_update_streamer_genres():
    data = await request.get_json()
    print(data)
    async with local_data_access() as _streamer_dal:
        await _streamer_dal.update_streamer_genres(data)
    return "done updating"
