"""Web app for the index future simulator.

Run it with:  python app.py   then open http://127.0.0.1:5000
For development with auto-reload:  flask --app app run --debug
In production use a real server, for example:  gunicorn app:app

The browser keeps the settings and the list of moves played so far, and sends
them to the server. The server replays the game with simulator.py and sends
back the table to show. Open /?lang=fr for the French version.
"""

from flask import Flask, jsonify, render_template, request

import simulator
from translations import DEFAULT_LANGUAGE, TEXT

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # requests are tiny: refuse big ones

MAX_PATHS = 10000  # most scenarios allowed in one Monte Carlo run (about 1 second)


def read_json(request_body):
    """The JSON object sent by the browser."""
    if not isinstance(request_body, dict):
        raise ValueError("The request body must be a JSON object.")
    return request_body


def read_moves(moves, settings):
    """Check the moves sent by the browser. Missing random numbers are drawn here."""
    if not isinstance(moves, list) or len(moves) > settings["steps"]:
        raise ValueError(f"'moves' must be a list of at most {settings['steps']} moves.")

    clean_moves = []
    for move in moves:
        if not isinstance(move, dict):
            raise ValueError("Each move must be an object.")

        correlation = move.get("correlation")
        if not simulator.is_number(correlation) or not -1 <= correlation <= 1:
            raise ValueError("'correlation' must be a number between -1 and 1.")

        change = move.get("change")
        if change is None:
            change = simulator.random_change(settings)
        elif not simulator.is_number(change) or not -0.5 <= change <= 0.5:
            raise ValueError("'change' must be a number between -0.5 and 0.5.")

        noise = move.get("noise")
        if noise is None:
            noise = simulator.random_noise()
        elif not simulator.is_number(noise) or not -10 <= noise <= 10:
            raise ValueError("'noise' must be a number between -10 and 10.")

        clean_moves.append({"change": change, "correlation": correlation, "noise": noise})
    return clean_moves


@app.route("/")
def home():
    language = request.args.get("lang", DEFAULT_LANGUAGE)
    if language not in TEXT:
        language = DEFAULT_LANGUAGE
    return render_template("index.html", t=TEXT[language], lang=language)


@app.route("/api/settings")
def api_settings():
    return jsonify({
        "defaults": simulator.DEFAULT_SETTINGS,
        "limits": simulator.LIMITS,
        "fixed": {
            "point_value": simulator.POINT_VALUE,
            "start_price": simulator.START_PRICE,
            "start_rate": simulator.START_RATE,
        },
    })


@app.route("/api/play", methods=["POST"])
def api_play():
    data = read_json(request.get_json(silent=True))
    settings = simulator.check_settings(data.get("settings"))
    moves = read_moves(data.get("moves"), settings)
    rows = simulator.play(moves, settings)
    return jsonify({
        "moves": moves,  # sent back because random numbers were filled in
        "rows": rows,
        "summary": simulator.compare(rows),
        "maintenance_margin": simulator.maintenance_margin(settings),
    })


@app.route("/api/monte-carlo", methods=["POST"])
def api_monte_carlo():
    data = read_json(request.get_json(silent=True))
    settings = simulator.check_settings(data.get("settings"))

    paths = data.get("paths", 2000)
    if not isinstance(paths, int) or isinstance(paths, bool) or not 1 <= paths <= MAX_PATHS:
        raise ValueError(f"'paths' must be a whole number between 1 and {MAX_PATHS}.")

    results = simulator.monte_carlo(paths, settings=settings)
    return jsonify({"paths": paths, "results": results})


@app.errorhandler(ValueError)
def bad_request(error):
    return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run()
