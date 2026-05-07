def test_frontend_origin_preflight_is_allowed(client):
    response = client.options(
        "/api/v1/portfolio/summary",
        headers={
            "Origin": "http://localhost:4400",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4400"


def test_frontend_origin_get_includes_cors_header(client):
    response = client.get(
        "/api/v1/portfolio/summary",
        headers={"Origin": "http://localhost:4400"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4400"
