import os
import httpx
import gidgetlab.routing
import gidgetlab.sansio
import gidgetlab.httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

router = gidgetlab.routing.Router()


@router.register("Issue Hook", action="open")
async def issue_opened_event(event, gl, *args, **kwargs):
    """Whenever an issue is opened, greet the author and say thanks."""
    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}/notes"
    message = f"Thanks for the report @{event.data['user']['username']}! I will look into it ASAP! (I'm a bot)."
    await gl.post(url, data={"body": message})


async def webhook(request: Request) -> Response:
    """Handler that processes GitLab webhook requests"""
    body = await request.body()
    secret = os.environ.get("GL_SECRET")
    event = gidgetlab.sansio.Event.from_http(request.headers, body, secret=secret)
    async with httpx.AsyncClient() as client:
        gl = gidgetlab.httpx.GitLabAPI(
            client, "gidgetlab", access_token=os.environ.get("GL_ACCESS_TOKEN")
        )
        await router.dispatch(event, gl)
    return Response(status_code=200)


app = Starlette(routes=[Route("/", webhook, methods=["POST"])])
