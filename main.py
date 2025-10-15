#
#  Import LIBRARIES
# import random
# import string

import time
from collections import defaultdict

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

#  Import FILES
#


app: FastAPI = FastAPI()


class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app=app)
        self.rate_limit_records: dict[str, float] = defaultdict(float)

    async def log_message(self, message: str) -> None:
        print(message)

    async def dispatch(self, request: Request, call_next) -> Response | None:
        client_ip: str = request.client.host
        current_time: float = time.time()
        if current_time - self.rate_limit_records[client_ip] < 1:  # 1 request per second limit
            return Response(content="Rate limit exceeded", status_code=429)

        self.rate_limit_records[client_ip] = current_time
        path: str = request.url.path
        await self.log_message(message=f"Request to {path}")

        # Process the request
        start_time: float = time.time()
        response: Response = await call_next(request)
        process_time: float = time.time() - start_time

        # Add custom headers without modifying the original headers object
        custom_headers: dict[str, str] = {"X-Process-Time": str(object=process_time)}
        for header, value in custom_headers.items():
            response.headers.append(key=header, value=value)

        # Asynchronous logging for processing time
        await self.log_message(message=f"Response for {path} took {process_time} seconds")

        return response


# Add the advanced middleware to the app
app.add_middleware(middleware_class=AdvancedMiddleware)


@app.get(path="/")
async def main() -> dict[str, str]:
    return {"message": "Hello, World!"}
