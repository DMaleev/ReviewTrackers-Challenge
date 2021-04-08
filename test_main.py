from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_valid_link():
    response = client.get("/?base_url=https%3A%2F%2Fwww.lendingtree.com%2Freviews%2Fmortgage%2Ffirst-midwest-bank%2F49832469")
    assert response.status_code == 200

def test_invalid_link():
    response = client.get("/?base_url=https%3A%2F%2Fwww.lengtree.com%2Freviews%2Fmortgage%2Ffirst-midwest-bank%2F49832469")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 400,
        "detail": "Invalid url format",
        "headers": None
        }

def test_no_review():
    response = client.get("/base_url=https%3A%2F%2Fwww.lendingtree.com%2Freviews%2Fmortgage%2Fgrander-home-loans-inc%2F58426565")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}