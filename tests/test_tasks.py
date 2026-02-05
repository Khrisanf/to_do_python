from app.models import TaskStatus


def register_and_login(client):
    response = client.post(
        "/auth/register",
        json={"username": "admin", "full_name": "Admin", "password": "secret123"},
    )
    assert response.status_code == 201
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "secret123"},
    )
    assert response.status_code == 200
    return response.json()["token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_task_crud_and_analytics(client):
    token = register_and_login(client)

    create_response = client.post(
        "/tasks",
        headers=auth_header(token),
        json={
            "title": "Первая задача",
            "description": "Описание",
            "status": TaskStatus.new.value,
            "topic": "аналитика",
        },
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["id"]

    list_response = client.get("/tasks", headers=auth_header(token))
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    filter_response = client.get(
        "/tasks",
        headers=auth_header(token),
        params={"status": TaskStatus.new.value, "topic": "аналитика"},
    )
    assert filter_response.status_code == 200
    assert len(filter_response.json()) == 1

    update_response = client.put(
        f"/tasks/{task_id}",
        headers=auth_header(token),
        json={"status": TaskStatus.in_progress.value},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == TaskStatus.in_progress.value

    status_response = client.patch(
        f"/tasks/{task_id}/status",
        headers=auth_header(token),
        json=TaskStatus.done.value,
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == TaskStatus.done.value

    analytics_response = client.get(
        "/tasks/analytics",
        headers=auth_header(token),
        params={"group_by": "status", "with_chart": True},
    )
    assert analytics_response.status_code == 200
    payload = analytics_response.json()
    assert payload["group_by"] == "status"
    assert payload["total"] == 1
    assert payload["data"][0]["count"] == 1
    assert payload["chart_base64"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_header(token),
    )
    assert delete_response.status_code == 204
