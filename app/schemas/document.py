from pydantic import BaseModel, HttpUrl


class IngestUrlRequest(BaseModel):
    url: HttpUrl
