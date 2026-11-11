import statistics

import pytest

import simulator


def moves(*changes, correlation=1, noise=0):
    """Build a list of moves: moves(0.02, -0.02) = up 2%, then down 2%."""
    return [{"change": c, "correlation": correlation, "noise": noise} for c in changes]


def test_no_moves_means_no_rows():
    assert simulator.play([]) == []


def test_a_gain_is_paid_right_away():
    row = simulator.play(moves(0.02))[0]
    assert row["cash"] == pytest.approx(5000)       # 100 points x $50
    assert row["balance"] == pytest.approx(30000)   # 25,000 + 5,000
    assert row["margin_call"] == 0


def test_a_small_loss_needs_no_margin_call():
    row = simulator.play(moves(-0.01))[0]           # -50 points = -$2,500
    assert row["cash"] == pytest.approx(-2500)
    assert row["balance"] == pytest.approx(22500)   # exactly at the limit: no call
    assert row["margin_call"] == 0


def test_a_big_loss_triggers_a_margin_call():
    row = simulator.play(moves(-0.02))[0]           # -$5,000 -> 20,000 is below 22,500
    assert row["margin_call"] == pytest.approx(5000)
    assert row["balance"] == pytest.approx(25000)   # topped back up


def test_the_margin_settings_are_used():
    settings = {"start_margin": 10000, "maintenance_ratio": 70}   # call level: $7,000
    row = simulator.play(moves(-0.02), settings)[0]               # -$5,000 -> 5,000 < 7,000
    assert row["margin_call"] == pytest.approx(5000)
    assert row["balance"] == pytest.approx(10000)
    assert simulator.maintenance_margin(simulator.check_settings(settings)) == 7000


# ---------------------------------------------------------------------------
# Short position
# ---------------------------------------------------------------------------
def test_a_short_position_is_the_mirror_image():
    long_rows = simulator.play(moves(0.02, -0.03, 0.01))
    short_rows = simulator.play(moves(0.02, -0.03, 0.01), {"position": "short"})
    for long_row, short_row in zip(long_rows, short_rows):
        assert short_row["cash"] == pytest.approx(-long_row["cash"])
        assert short_row["interest"] == pytest.approx(-long_row["interest"])


def test_a_short_position_loses_when_the_index_rises():
    row = simulator.play(moves(0.02), {"position": "short"})[0]
    assert row["cash"] == pytest.approx(-5000)
    assert row["margin_call"] == pytest.approx(5000)


# ---------------------------------------------------------------------------
# Interest rate and correlation
# ---------------------------------------------------------------------------
def test_with_a_correlation_of_one_the_rate_follows_the_index():
    assert simulator.play(moves(0.02, correlation=1))[0]["rate"] == pytest.approx(4.5)
    assert simulator.play(moves(-0.02, correlation=1))[0]["rate"] == pytest.approx(3.5)


def test_with_a_correlation_of_minus_one_the_rate_goes_the_other_way():
    assert simulator.play(moves(0.02, correlation=-1))[0]["rate"] == pytest.approx(3.5)


def test_with_no_correlation_and_no_noise_the_rate_stays_put():
    assert simulator.play(moves(0.02, correlation=0, noise=0))[0]["rate"] == pytest.approx(4.0)


def test_with_no_correlation_the_rate_moves_with_its_own_noise():
    row = simulator.play(moves(0.02, correlation=0, noise=1))[0]
    assert row["rate"] == pytest.approx(4.0 + 0.75)   # one rate volatility up


@pytest.mark.parametrize("wanted", [-1, -0.5, 0, 0.5, 1])
def test_the_correlation_is_a_real_correlation(wanted):
    # Many random steps: the measured correlation between the index move and
    # the rate move must be the one we asked for.
    import random
    rng = random.Random(1)
    settings = simulator.check_settings()
    changes = [rng.gauss(0, 0.03) for _ in range(20000)]
    rate_moves = []
    for change in changes:
        rate = simulator.new_rate(4.0, change, wanted, rng.gauss(0, 1), settings)
        rate_moves.append(rate - 4.0)
    assert statistics.correlation(changes, rate_moves) == pytest.approx(wanted, abs=0.03)


def test_the_rate_never_goes_below_zero():
    rows = simulator.play(moves(-0.5, -0.5, -0.5))
    assert all(row["rate"] >= 0 for row in rows)


def test_each_step_can_have_its_own_correlation():
    rows = simulator.play([
        {"change": 0.02, "correlation": 1, "noise": 0},    # rate 4.0 -> 4.5
        {"change": 0.02, "correlation": -1, "noise": 0},   # rate 4.5 -> 4.0
    ])
    assert rows[1]["old_rate"] == pytest.approx(4.5)
    assert rows[1]["rate"] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Interest, future and forward
# ---------------------------------------------------------------------------
def test_interest_by_hand():
    rows = simulator.play(moves(0.02, -0.02))
    # Step 1: +$5,000 invested for 1 step at 4.5% a year, 1/12 of a year per step.
    assert rows[0]["interest"] == pytest.approx(5000 * 0.045 / 12 * 1)
    # Step 2 is the last step: no time left to earn interest.
    assert rows[1]["interest"] == 0


def test_future_is_forward_plus_interest():
    rows = simulator.play(moves(0.03, -0.01, 0.02, -0.04))
    result = simulator.compare(rows)
    last_price = rows[-1]["price"]
    assert result["forward"] == pytest.approx((last_price - 5000) * 50)
    assert result["future"] == pytest.approx(result["forward"] + result["gap"])


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def test_missing_settings_get_their_default():
    assert simulator.check_settings(None) == simulator.DEFAULT_SETTINGS
    assert simulator.check_settings({"steps": 6})["volatility"] == 3.0


@pytest.mark.parametrize("bad", [
    {"steps": 3},
    {"steps": 25},
    {"steps": 12.5},
    {"steps": "12"},
    {"volatility": 0},
    {"rate_volatility": 5},
    {"start_margin": True},
    {"maintenance_ratio": 100},
    {"position": "flat"},
    {"unknown": 1},
    {"volatility": float("nan")},
])
def test_bad_settings_are_refused(bad):
    with pytest.raises(ValueError):
        simulator.check_settings(bad)


def test_settings_must_be_an_object():
    with pytest.raises(ValueError):
        simulator.check_settings([1, 2])


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------
def test_monte_carlo_sign_follows_the_correlation():
    negative, zero, positive = simulator.monte_carlo(3000, seed=42)
    assert positive["average"] > 0 > negative["average"]
    assert abs(zero["average"]) < 4 * zero["error"] + 1   # close to zero
    assert 200 < positive["average"] < 450                 # about +$310
    assert -450 < negative["average"] < -200               # about -$310


def test_monte_carlo_price_gap_is_the_average_in_points():
    positive = simulator.monte_carlo(500, correlations=(1,), seed=3)[0]
    assert positive["price_gap"] == pytest.approx(positive["average"] / 50)


def test_monte_carlo_for_a_short_position():
    long_side = simulator.monte_carlo(500, correlations=(1,), seed=3)[0]
    short = {"position": "short"}
    short_side = simulator.monte_carlo(500, correlations=(1,), settings=short, seed=3)[0]
    assert short_side["average"] == pytest.approx(-long_side["average"])   # the mirror image
    assert short_side["price_gap"] == pytest.approx(long_side["price_gap"])  # same price gap


def test_monte_carlo_gives_the_same_result_with_the_same_seed():
    assert simulator.monte_carlo(200, seed=7) == simulator.monte_carlo(200, seed=7)
