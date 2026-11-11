import pytest

from app import app
from translations import TEXT


@pytest.fixture()
def client():
    return app.test_client()


def move(change=0.02, correlation=1, noise=0):
    return {"change": change, "correlation": correlation, "noise": noise}


def post_play(client, moves, settings=None):
    body = {"moves": moves}
    if settings is not None:
        body["settings"] = settings
    return client.post("/api/play", json=body)


# ---------------------------------------------------------------------------
# Pages and languages
# ---------------------------------------------------------------------------
def test_home_page_and_static_files(client):
    page = client.get("/")
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "daily settlement" in html
    assert '<html lang="en">' in html
    for path in ("/static/app.js", "/static/style.css", "/static/vendor/chart.umd.js"):
        response = client.get(path)
        assert response.status_code == 200, path
        response.close()


def test_french_page(client):
    html = client.get("/?lang=fr").get_data(as_text=True)
    assert '<html lang="fr">' in html
    assert "règlement quotidien" in html


def test_unknown_language_falls_back_to_english(client):
    html = client.get("/?lang=xx").get_data(as_text=True)
    assert '<html lang="en">' in html


def test_both_languages_have_the_same_texts():
    en, fr = TEXT["en"], TEXT["fr"]
    assert set(en) == set(fr)
    assert len(en["guide"]) == len(fr["guide"])
    assert len(en["tour"]) == len(fr["tour"])
    for stage_en, stage_fr in zip(en["tour"], fr["tour"]):
        assert set(stage_en) == set(stage_fr)
        assert len(stage_en["options"]) == len(stage_fr["options"])
        assert stage_en["answer"] == stage_fr["answer"]


# ---------------------------------------------------------------------------
# /api/settings and /api/play
# ---------------------------------------------------------------------------
def test_settings(client):
    data = client.get("/api/settings").get_json()
    assert data["defaults"]["steps"] == 12
    assert data["limits"]["steps"] == [4, 24]
    assert data["fixed"]["point_value"] == 50


def test_play_with_no_moves(client):
    data = post_play(client, []).get_json()
    assert data["rows"] == []
    assert data["maintenance_margin"] == 22500


def test_play_with_moves(client):
    data = post_play(client, [move()]).get_json()
    assert len(data["rows"]) == 1
    assert data["rows"][0]["cash"] == pytest.approx(5000)
    assert data["rows"][0]["rate"] == pytest.approx(4.5)
    assert data["summary"]["forward"] == pytest.approx(5000)


def test_play_uses_the_settings(client):
    data = post_play(client, [move()], {"position": "short", "steps": 6}).get_json()
    assert data["rows"][0]["cash"] == pytest.approx(-5000)
    assert post_play(client, [move()] * 7, {"steps": 6}).status_code == 400


def test_missing_random_numbers_are_filled_in(client):
    moves = [{"change": None, "correlation": 0.5, "noise": None}] * 12
    data = post_play(client, moves).get_json()
    assert len(data["rows"]) == 12
    for sent_back in data["moves"]:
        assert -0.5 < sent_back["change"] < 0.5
        assert sent_back["noise"] is not None


def test_too_many_moves_is_refused(client):
    response = post_play(client, [move()] * 13)
    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.parametrize("bad_move", [
    {"change": 0.9, "correlation": 0, "noise": 0},      # change too big
    {"change": "x", "correlation": 0, "noise": 0},      # not a number
    {"change": True, "correlation": 0, "noise": 0},     # a boolean is not a number
    {"change": 0.01, "correlation": 2, "noise": 0},     # correlation out of range
    {"change": 0.01, "noise": 0},                       # correlation missing
    {"change": 0.01, "correlation": 0, "noise": 99},    # noise out of range
    "not a move",
])
def test_bad_moves_are_refused(client, bad_move):
    response = post_play(client, [bad_move])
    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.parametrize("bad_settings", [
    {"steps": 99},
    {"position": "flat"},
    {"nothing": 1},
    [1, 2],
])
def test_bad_settings_are_refused(client, bad_settings):
    response = post_play(client, [], bad_settings)
    assert response.status_code == 400


def test_a_body_that_is_not_json_is_refused(client):
    response = client.post("/api/play", data="hello")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# /api/monte-carlo
# ---------------------------------------------------------------------------
def test_monte_carlo(client):
    data = client.post("/api/monte-carlo", json={"paths": 1000}).get_json()
    assert data["paths"] == 1000
    gaps = {r["correlation"]: r for r in data["results"]}
    assert gaps[1]["average"] > 0 > gaps[-1]["average"]
    assert gaps[1]["price_gap"] > 0


def test_monte_carlo_uses_the_settings(client):
    body = {"paths": 500, "settings": {"position": "short"}}
    data = client.post("/api/monte-carlo", json=body).get_json()
    gaps = {r["correlation"]: r for r in data["results"]}
    assert gaps[1]["average"] < 0 < gaps[1]["price_gap"]


@pytest.mark.parametrize("paths", [0, -5, 10**9, "many", True])
def test_monte_carlo_refuses_bad_paths(client, paths):
    response = client.post("/api/monte-carlo", json={"paths": paths})
    assert response.status_code == 400
