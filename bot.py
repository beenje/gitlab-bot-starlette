import datetime
import os
import httpx
import gidgetlab.routing
import gidgetlab.sansio
import gidgetlab.httpx
from starlette.applications import Starlette
from starlette.background import BackgroundTask
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


@router.register("Push Hook")
async def dummy_action_on_push(event, gl, *args, **kwargs):
    print(f"Received {event.event}")
    print(f"Triggering some action at {datetime.datetime.utcnow()}...")
    await gl.sleep(5)
    print(f"Action done at {datetime.datetime.utcnow()}")


async def create_client() -> None:
    """Startup handler that creates the GitLabAPI instance"""
    client = httpx.AsyncClient()
    app.state.gl = gidgetlab.httpx.GitLabAPI(
        client, "gidgetlab", access_token=os.environ.get("GL_ACCESS_TOKEN")
    )


async def close_client() -> None:
    """Shutdown handler that closes the httpx client"""
    await app.state.gl._client.aclose()


async def webhook(request: Request) -> Response:
    """Handler that processes GitLab webhook requests"""
    body = await request.body()
    secret = os.environ.get("GL_SECRET")
    event = gidgetlab.sansio.Event.from_http(request.headers, body, secret=secret)
    task = BackgroundTask(router.dispatch, event, request.app.state.gl)
    return Response(status_code=200, background=task)


app = Starlette(
    routes=[Route("/", webhook, methods=["POST"])],
    on_startup=[create_client],
    on_shutdown=[close_client],
)
