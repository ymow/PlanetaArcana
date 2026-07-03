"""帳號與占卜歸屬測試"""

from app.core.auth import create_access_token
from app.models.user import User


def _create_user(db_session, email: str) -> User:
    user = User(email=email, name=email.split("@", 1)[0])
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_me_returns_current_user(client, auth_headers, test_user):
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == test_user.id
    assert response.json()["email"] == test_user.email


def test_authenticated_divine_is_bound_to_user(client, divine_payload, auth_headers, test_user):
    created = client.post("/api/divines", json=divine_payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["user_id"] == test_user.id

    own_history = client.get("/api/divines", headers=auth_headers)
    assert own_history.status_code == 200
    assert [item["id"] for item in own_history.json()] == [created.json()["id"]]

    anonymous_history = client.get("/api/divines")
    assert anonymous_history.status_code == 200
    assert anonymous_history.json() == []


def test_user_owned_divine_is_private(
    client, db_session, divine_payload, auth_headers
):
    owner_created = client.post(
        "/api/divines", json=divine_payload, headers=auth_headers
    )
    divine_id = owner_created.json()["id"]

    other = _create_user(db_session, "other@example.com")
    other_headers = {"Authorization": f"Bearer {create_access_token(other)}"}

    assert client.get(f"/api/divines/{divine_id}").status_code == 404
    assert client.get(f"/api/divines/{divine_id}", headers=other_headers).status_code == 404


def test_claim_anonymous_divine(client, divine_payload, auth_headers, test_user):
    created = client.post("/api/divines", json=divine_payload)
    divine_id = created.json()["id"]
    assert created.json()["user_id"] is None

    claimed = client.post(f"/api/divines/{divine_id}/claim", headers=auth_headers)
    assert claimed.status_code == 200
    assert claimed.json()["user_id"] == test_user.id

    own_history = client.get("/api/divines", headers=auth_headers).json()
    assert [item["id"] for item in own_history] == [divine_id]
