
def test_homepage(summary_app):
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200