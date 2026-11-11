"""Browser tests: they click through the real page.

They need Playwright:   pip install playwright && playwright install chromium
If Playwright or a browser is missing, these tests are skipped.
To use a Chrome or Chromium you already have, set CHROME_PATH to its location.
"""

import os
import threading

import pytest
from werkzeug.serving import make_server

from app import app

playwright = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def base_url():
    """Run the app on a free port while the tests of this file run."""
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    with playwright.sync_playwright() as p:
        options = {"args": ["--no-sandbox", "--no-proxy-server"]}
        if os.environ.get("CHROME_PATH"):
            options["executable_path"] = os.environ["CHROME_PATH"]
        try:
            browser = p.chromium.launch(**options)
        except Exception as error:
            pytest.skip(f"No browser available: {error}")
        yield browser
        browser.close()


@pytest.fixture()
def page(browser, base_url):
    page = browser.new_page(viewport={"width": 900, "height": 1400})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(base_url, wait_until="networkidle")
    wait_for_step(page, 0)
    yield page
    page.close()
    assert errors == [], "The page reported errors"


def wait_for_step(page, number):
    """Wait until the 'Step' tile shows 'number / ...'."""
    page.wait_for_function(
        f"document.querySelector('#t-n').textContent.trim().startsWith('{number} /')"
    )


def click(page, action):
    page.click(f"[data-action={action}]")


def text(page, selector):
    return page.inner_text(selector)


# ---------------------------------------------------------------------------
# The game
# ---------------------------------------------------------------------------
def test_first_screen(page):
    assert "You are long one S&P 500 future" in text(page, "#msg")
    assert text(page, "#t-n") == "0 / 12"
    assert text(page, "#t-b") == "$25,000"
    assert "No step played yet." in text(page, "#tb")
    assert page.locator("canvas").count() == 3


def test_a_gain_then_losses_trigger_a_margin_call(page):
    click(page, "up")
    wait_for_step(page, 1)
    assert text(page, "#t-f") == "5,100"
    assert text(page, "#t-r") == "4.50%"
    assert text(page, "#t-b") == "$30,000"
    assert "You gain $5,000" in text(page, "#msg")
    assert "works in your favor" in text(page, "#msg")

    for step in (2, 3, 4):
        click(page, "down")
        wait_for_step(page, step)
    assert "margin call, you deposit" in text(page, "#msg")
    assert "(margin call" in text(page, "#tb")
    assert page.locator("#tb tr").count() == 4


def test_undo_and_restart(page):
    click(page, "up")
    wait_for_step(page, 1)
    click(page, "down")
    wait_for_step(page, 2)
    click(page, "undo")
    wait_for_step(page, 1)
    click(page, "reset")
    wait_for_step(page, 0)
    click(page, "undo")   # nothing to undo: stays at the start
    wait_for_step(page, 0)


def test_play_to_maturity(page):
    click(page, "auto")
    wait_for_step(page, 12)
    assert page.locator("#tb tr").count() == 12
    assert "played to maturity" in text(page, "#msg")
    click(page, "up")
    page.wait_for_function(
        "document.querySelector('#msg').textContent.includes('Maturity reached')"
    )


def test_a_short_position_loses_when_the_index_rises(page):
    page.click("summary:has-text('Settings')")
    page.check("input[name=position][value=short]")
    page.wait_for_function("document.querySelector('#msg').textContent.includes('short')")
    click(page, "up")
    wait_for_step(page, 1)
    assert "You lose $5,000" in text(page, "#msg")


def test_changing_a_setting_restarts_the_game(page):
    click(page, "up")
    wait_for_step(page, 1)
    page.click("summary:has-text('Settings')")
    page.evaluate("""() => {
        const slider = document.getElementById('s-steps');
        slider.value = 6;
        slider.dispatchEvent(new Event('input'));
        slider.dispatchEvent(new Event('change'));
    }""")
    page.wait_for_function("document.querySelector('#t-n').textContent.trim() === '0 / 6'")
    assert text(page, "#o-steps") == "6"


def test_correlation_changes_the_rate_reaction(page):
    page.evaluate("""() => {
        const slider = document.getElementById('corr');
        slider.value = -1;
        slider.dispatchEvent(new Event('input'));
    }""")
    assert "negative" in text(page, "#corr-out")
    click(page, "up")
    wait_for_step(page, 1)
    assert text(page, "#t-r") == "3.50%"   # the index rose, the rate fell
    assert "works against you" in text(page, "#msg")


def test_monte_carlo(page):
    click(page, "mc")
    page.wait_for_selector(".mc-row")
    rows = page.locator(".mc-row")
    assert rows.count() == 3
    assert "pts" in rows.nth(2).inner_text()
    assert "−$" in rows.nth(0).inner_text()    # negative correlation: negative gap
    assert "+$" in rows.nth(2).inner_text()    # positive correlation: positive gap


# ---------------------------------------------------------------------------
# Sharing, CSV, language, guided tour
# ---------------------------------------------------------------------------
def test_share_link_brings_the_same_game_back(page, browser):
    click(page, "up")
    wait_for_step(page, 1)
    click(page, "down")
    wait_for_step(page, 2)
    click(page, "share")
    page.wait_for_function(
        "document.querySelector('#msg').textContent.includes('Link copied') || "
        "document.querySelector('#msg').textContent.includes('Copy this link')"
    )
    link = page.evaluate(
        "location.origin + location.pathname + '?lang=' + LANG + '#g=' + encodeGame()"
    )
    balance = text(page, "#t-b")

    other = browser.new_page()
    other.goto(link, wait_until="networkidle")
    wait_for_step(other, 2)
    assert text(other, "#t-b") == balance
    other.close()


def test_csv_download(page):
    click(page, "up")
    wait_for_step(page, 1)
    click(page, "down")
    wait_for_step(page, 2)
    with page.expect_download() as download_info:
        click(page, "csv")
    lines = open(download_info.value.path(), encoding="utf-8").read().strip().split("\n")
    assert lines[0].startswith("step,index_change_pct")
    assert len(lines) == 3
    assert lines[1].startswith("1,2.00,1,4.500,5000.00,30000.00,0.00,")


def test_french_version_and_language_switch_keeps_the_game(page):
    click(page, "up")
    wait_for_step(page, 1)
    page.click("[data-lang=fr]")
    page.wait_for_function("document.documentElement.lang === 'fr'")
    wait_for_step(page, 1)
    assert "Étape 1" in text(page, "#msg")
    assert "Tu gagnes" in text(page, "#msg")
    assert "$" in text(page, "#t-b")


def test_guided_tour(page):
    click(page, "tour")
    page.wait_for_function("document.querySelector('#tour-stage').textContent === 'Stage 1 of 6'")
    assert page.is_visible("#tour")

    # a wrong answer, then the right one
    page.locator("#tour-options button").nth(0).click()
    assert "wrong" in page.get_attribute("#tour-feedback", "class")
    page.locator("#tour-options button").nth(1).click()
    assert "right" in page.get_attribute("#tour-feedback", "class")

    expected_steps = [1, 2, 3, 4, 12]
    for stage, step in enumerate(expected_steps, start=2):
        page.click("#tour-next")
        page.wait_for_function(
            f"document.querySelector('#tour-stage').textContent === 'Stage {stage} of 6'"
        )
        wait_for_step(page, step)
        if stage == 4:   # the margin call stage
            assert "$25,000" in text(page, "#tour-text")
            assert "(margin call" in text(page, "#tb")

    assert text(page, "#tour-next") == "Finish"
    page.click("#tour-next")
    assert page.is_hidden("#tour")


def test_leaving_the_tour_by_playing(page):
    click(page, "tour")
    page.wait_for_selector("#tour:not([hidden])")
    click(page, "up")
    wait_for_step(page, 1)
    assert page.is_hidden("#tour")
