from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware #cors middleware
from starlette.middleware.httpsredirect import (  # noqa  - https redirect
    HTTPSRedirectMiddleware as HTTPSRedirectMiddleware,
)
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.user_router import router

app = FastAPI()

# middleware
origins = [ 
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  라우터
app.include_router(router, tags=['register'])


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)