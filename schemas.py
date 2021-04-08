from pydantic import BaseModel
from typing import List

class ReviewBase(BaseModel):
    title: str
    text: str
    consumerName: str
    consumerFrom: str
    consumerReviewDate: str
    stars: int

class Reviews(BaseModel):
    total: int
    reviews: List[ReviewBase]