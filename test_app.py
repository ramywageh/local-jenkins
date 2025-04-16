import pytest
from app import app, tasks

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Todo-list' in response.data

def test_add_task(client):
    response = client.post('/add', data={'task': 'Test Task'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Task' in response.data

def test_delete_task(client):
    tasks.append('Task to be deleted')
    task_id = len(tasks) - 1
    response = client.get(f'/delete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Task to be deleted' not in response.data