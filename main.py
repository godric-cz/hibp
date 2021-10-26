from fastapi import FastAPI
from fastapi.param_functions import Path
from pydantic import BaseModel, Field
from starlette.responses import PlainTextResponse

from search import Search

app = FastAPI()
search = Search('data/index.bin', 'data/passwords.bin')
search.__enter__()


class CheckRequest(BaseModel):
    sha1: str = Field(
        ...,
        regex='^[0-9a-fA-F]{40}$',
        example='2AAE6C35C94FCFB415DBE95F408B9CE91EE846ED'
    )


class CheckResponse(BaseModel):
    occurences: int


@app.post('/check', response_model=CheckResponse)
def check(req: CheckRequest):
    return {"occurences": search.search(req.sha1)}


@app.get('/range/{prefix}')
def range(prefix: str = Path(..., regex='^[0-9a-fA-F]{5}$', example='21BD1')):
    return PlainTextResponse(search.list(prefix))
