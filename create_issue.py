import asyncio
import os
import httpx
import gidgetlab.httpx


async def main():
    async with httpx.AsyncClient() as client:
        gl = gidgetlab.httpx.GitLabAPI(
            client, "gidgetlab", access_token=os.environ.get("GL_ACCESS_TOKEN")
        )
        await gl.post(
            "/projects/beenje%2Fstrange-relationship/issues",
            data={
                "title": "We got a problem",
                "description": "You should use HTTPX!",
            })


asyncio.run(main())
