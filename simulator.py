"""Index future simulator: daily settlement, margin calls and interest.

How it works (simplified):
- You buy (long) or sell (short) 1 future on an index. Each index point is
  worth $50.
- At every step the index moves. The gain or loss is paid in cash right away
  (this is the "daily settlement").
- Your margin account starts at $25,000. If it falls below 90% of that, you
  must top it back up to $25,000 (this is the "margin call").
- The interest rate also moves at every step. A "correlation" between -1 and
  +1 says how much the rate moves together with the index.
- A gain is invested at that day's rate, a loss is borrowed at that day's rate,
  until the end. A forward pays nothing before the end, so the gap between the
  future and the forward is just this interest.

The size of the gap depends on the volatility settings, which are only
illustrative. Its sign depends on the correlation and on your position.
"""

import math
import random
import statistics

# ---------------------------------------------------------------------------
# Fixed numbers
# ---------------------------------------------------------------------------
POINT_VALUE = 50       # dollars per index point
START_PRICE = 5000     # futures price at step 0
START_RATE = 4.0       # interest rate at step 0, in %
STEPS_PER_YEAR = 12    # we count one step as one month of interest

# ---------------------------------------------------------------------------
# Settings the user can change in the web page
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "steps": 12,               # number of steps until maturity
    "volatility": 3.0,         # typical index move per step, in %
    "rate_volatility": 0.75,   # typical rate move per step, in percentage points
    "start_margin": 25000,     # money in the margin account at step 0
    "maintenance_ratio": 90,   # margin call level, in % of the start margin
    "position": "long",        # "long" = you bought, "short" = you sold
}

# Allowed range of each number: name -> (minimum, maximum)
LIMITS = {
    "steps": (4, 24),
    "volatility": (1, 6),
    "rate_volatility": (0.25, 1.5),
    "start_margin": (10000, 50000),
    "maintenance_ratio": (70, 95),
}


def is_number(value):
    """True for ints and floats (True and False do not count)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_settings(given=None):
    """Return complete settings (missing ones get their default value).

    Raises ValueError if something is wrong.
    """
    if given is None:
        given = {}
    if not isinstance(given, dict):
        raise ValueError("'settings' must be an object.")

    settings = dict(DEFAULT_SETTINGS)
    for name, value in given.items():
        if name not in DEFAULT_SETTINGS:
            raise ValueError(f"Unknown setting '{name}'.")
        settings[name] = value

    for name, (low, high) in LIMITS.items():
        value = settings[name]
        if not is_number(value) or not low <= value <= high:
            raise ValueError(f"'{name}' must be a number between {low} and {high}.")

    if settings["steps"] != int(settings["steps"]):
        raise ValueError("'steps' must be a whole number.")
    settings["steps"] = int(settings["steps"])

    if settings["position"] not in ("long", "short"):
        raise ValueError("'position' must be 'long' or 'short'.")
    return settings


def maintenance_margin(settings):
    """Below this balance you get a margin call."""
    return settings["start_margin"] * settings["maintenance_ratio"] / 100


# ---------------------------------------------------------------------------
# One step of the game
# ---------------------------------------------------------------------------
def random_change(settings=None):
    """A random index move, for example 0.013 for +1.3%."""
    settings = check_settings(settings)
    return random.gauss(0, settings["volatility"] / 100)


def random_noise():
    """A random number from a standard normal law (the rate's own randomness)."""
    return random.gauss(0, 1)


def new_rate(rate, change, correlation, noise, settings):
    """The interest rate after one step (it never goes below 0).

    The rate shock is built from two parts:
    - the index move, in standard deviations, times the correlation;
    - an independent random number ("noise"), so that the final correlation
      between the index and the rate is really the one you chose.
    With a correlation of +1 the rate follows the index exactly,
    with 0 it moves on its own, with -1 it moves the opposite way.
    """
    index_shock = change / (settings["volatility"] / 100)
    own_shock = math.sqrt(1 - correlation ** 2) * noise
    rate_shock = correlation * index_shock + own_shock
    return max(rate + settings["rate_volatility"] * rate_shock, 0)


def play(moves, settings=None):
    """Play a game from its list of moves and return one row per step.

    A move looks like {"change": 0.02, "correlation": 1.0, "noise": 0.0}:
    the index goes up 2% and the rate follows it exactly.
    """
    settings = check_settings(settings)
    sign = 1 if settings["position"] == "long" else -1
    maintenance = maintenance_margin(settings)

    price = START_PRICE
    rate = START_RATE
    balance = settings["start_margin"]
    rows = []

    for step, move in enumerate(moves, start=1):
        old_price = price
        old_rate = rate
        price = old_price * (1 + move["change"])
        cash = sign * (price - old_price) * POINT_VALUE   # the daily settlement
        rate = new_rate(old_rate, move["change"], move["correlation"], move["noise"], settings)

        balance = balance + cash
        margin_call = 0
        if balance < maintenance:
            margin_call = settings["start_margin"] - balance   # cash you must deposit
            balance = settings["start_margin"]

        rows.append({
            "step": step,
            "change": move["change"],
            "correlation": move["correlation"],
            "price": price,
            "old_rate": old_rate,
            "rate": rate,
            "cash": cash,
            "balance": balance,
            "margin_call": margin_call,
        })

    # Interest on each cash flow: it is invested (or borrowed) at the rate of
    # its own step, from that step until the last step played.
    last_step = len(rows)
    for row in rows:
        steps_left = last_step - row["step"]
        row["interest"] = row["cash"] * row["rate"] / 100 / STEPS_PER_YEAR * steps_left

    return rows


def compare(rows):
    """Compare the future (cash + interest) with the forward (cash only, at the end)."""
    cash = sum(row["cash"] for row in rows)
    interest = sum(row["interest"] for row in rows)
    return {"future": cash + interest, "forward": cash, "gap": interest}


# ---------------------------------------------------------------------------
# Many games at once
# ---------------------------------------------------------------------------
def monte_carlo(paths=2000, correlations=(-1, 0, 1), settings=None, seed=None):
    """Average future - forward gap over many random games.

    Every correlation is tested on the same random games, so any difference
    between the results comes from the correlation itself.

    "price_gap" is the same gap in index points, seen from the long side: it is
    how far the future's price should sit above (+) or below (-) the forward's
    price to make up for the interest effect. It does not depend on your position.
    """
    settings = check_settings(settings)
    sign = 1 if settings["position"] == "long" else -1
    rng = random.Random(seed)

    games = []
    for _ in range(paths):
        changes = [rng.gauss(0, settings["volatility"] / 100) for _ in range(settings["steps"])]
        noises = [rng.gauss(0, 1) for _ in range(settings["steps"])]
        games.append((changes, noises))

    results = []
    for correlation in correlations:
        gaps = []
        for changes, noises in games:
            moves = [
                {"change": change, "correlation": correlation, "noise": noise}
                for change, noise in zip(changes, noises)
            ]
            gaps.append(compare(play(moves, settings))["gap"])

        average = statistics.mean(gaps)
        results.append({
            "correlation": correlation,
            "average": average,
            "error": statistics.pstdev(gaps) / len(gaps) ** 0.5,   # standard error
            "price_gap": average * sign / POINT_VALUE,
        })
    return results
