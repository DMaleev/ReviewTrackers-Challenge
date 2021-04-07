from pydantic import BaseModel

class Review(BaseModel):
    title: str
    text: str
    consumerName: str
    consumerReviewDate: str