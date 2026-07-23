# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------


def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Cover the CRUD routes",
            "priority": "High",
            "assignee": "Sam",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Sam"
    assert "id" in body and "created_at" in body and "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "priority": "Urgent"})
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "extra_field": "nope"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(
    client, created_task
):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low task", "priority": "Low"})
    client.post("/tasks", json={"title": "High task", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "High task"


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}
# ---------------------------------------------------------------------------


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created_task["id"]


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ---------------------------------------------------------------------------
# PATCH /tasks/{task_id}
# ---------------------------------------------------------------------------


def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}", json={"title": "Updated title"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated title"
    assert body["priority"] == created_task["priority"]
    assert body["status"] == created_task["status"]


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/does-not-exist", json={"title": "New title"})
    assert response.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}", json={"status": "InProgress"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    # created_task starts as ToDo; ToDo -> ToDo is a no-op and must be rejected.
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id}
# ---------------------------------------------------------------------------


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")
    assert response.status_code == 204
    assert response.content == b""

    follow_up = client.get(f"/tasks/{created_task['id']}")
    assert follow_up.status_code == 404


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/does-not-exist")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Feature: Due dates + overdue filter
# ---------------------------------------------------------------------------


def test_create_task_valid_due_date_returns_201(client):
    response = client.post(
        "/tasks", json={"title": "Ship report", "due_date": "2099-01-01"}
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == "2099-01-01"


def test_create_task_invalid_due_date_format_returns_422(client):
    response = client.post(
        "/tasks", json={"title": "Ship report", "due_date": "not-a-date"}
    )
    assert response.status_code == 422


def test_task_with_past_due_date_is_overdue(client):
    response = client.post(
        "/tasks", json={"title": "Late task", "due_date": "2000-01-01"}
    )
    assert response.status_code == 201
    assert response.json()["is_overdue"] is True


def test_done_task_with_past_due_date_is_not_overdue(client):
    create = client.post(
        "/tasks", json={"title": "Finished late", "due_date": "2000-01-01"}
    )
    task_id = create.json()["id"]
    # Move through the valid transition path: ToDo -> InProgress -> Done
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    done = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert done.status_code == 200
    assert done.json()["is_overdue"] is False


def test_update_due_date_returns_200_and_recomputes_overdue(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}", json={"due_date": "2000-01-01"}
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == "2000-01-01"
    assert response.json()["is_overdue"] is True


def test_filter_overdue_returns_only_overdue_tasks(client):
    client.post("/tasks", json={"title": "Overdue task", "due_date": "2000-01-01"})
    client.post("/tasks", json={"title": "Future task", "due_date": "2099-01-01"})
    client.post("/tasks", json={"title": "No due date"})

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Overdue task"


# ---------------------------------------------------------------------------
# Feature: Tags / labels
# ---------------------------------------------------------------------------


def test_create_task_with_tags_returns_201(client):
    response = client.post(
        "/tasks", json={"title": "Tagged task", "tags": ["backend", "urgent"]}
    )
    assert response.status_code == 201
    assert response.json()["tags"] == ["backend", "urgent"]


def test_create_task_rejects_blank_tag(client):
    response = client.post(
        "/tasks", json={"title": "Tagged task", "tags": ["backend", "   "]}
    )
    assert response.status_code == 422


def test_update_tags_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}", json={"tags": ["frontend"]}
    )
    assert response.status_code == 200
    assert response.json()["tags"] == ["frontend"]


def test_filter_by_tag_returns_only_matches(client):
    client.post("/tasks", json={"title": "Task A", "tags": ["backend"]})
    client.post("/tasks", json={"title": "Task B", "tags": ["frontend"]})

    response = client.get("/tasks", params={"tag": "backend"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Task A"


def test_tags_preserved_after_unrelated_update(client):
    create = client.post(
        "/tasks", json={"title": "Tagged task", "tags": ["backend"]}
    )
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"title": "Renamed task"})
    assert response.status_code == 200
    assert response.json()["tags"] == ["backend"]
