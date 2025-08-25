def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    expected_text = 'Merhaba, Akademik Yönetim Sistemi! API dokümantasyonu için /api/docs adresini ziyaret edin.'
    assert expected_text.encode('utf-8') in response.data