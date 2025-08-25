import pytest
from conftest import admin_token, student_token

def test_create_user_as_admin_succeeds(test_client, admin_token):
    """Admin rolündeki kullanıcının yeni kullanıcı oluşturabildiğini test eder."""
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    data = {
        'username': 'new_user_1',
        'email': 'new_user1@test.com',
        'password': 'password',
        'role_id': 1
    }
    response = test_client.post('/api/users', json=data, headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'

def test_create_user_as_student_fails(test_client, student_token):
    """Student rolündeki kullanıcının yeni kullanıcı oluşturamadığını test eder."""
    headers = {
        'Authorization': f'Bearer {student_token}'
    }
    data = {
        'username': 'new_user_2',
        'email': 'new_user2@test.com',
        'password': 'password',
        'role_id': 1
    }
    response = test_client.post('/api/users', json=data, headers=headers)
    assert response.status_code == 403  # Forbidden - Yasaklanmış

def test_create_user_without_token_fails(test_client):
    """Token olmadan yeni kullanıcı oluşturma denemesinin başarısız olduğunu test eder."""
    data = {
        'username': 'new_user_3',
        'email': 'new_user3@test.com',
        'password': 'password',
        'role_id': 1
    }
    response = test_client.post('/api/users', json=data)
    assert response.status_code == 401  # Unauthorized - Yetkilendirilmemiş