from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from config import (
    SYSTEM_PROMPT,
    CONFIDENTIAL_DATA
)

from llm import ask_llm

from attacks import (
    ATTACKS,
    get_attack
)

from defenses import (
    detect_injection,
    sanitize_output,
    build_safe_prompt
)

from evaluator import (
    evaluate_response,
    calculate_statistics
)

from baseline import run_vulnerable_baseline


app = Flask(__name__)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():
    statistics = calculate_statistics()

    return render_template(
        "index.html",
        attacks=ATTACKS,
        statistics=statistics
    )


# ============================================================
# RUN ATTACK
# ============================================================

@app.route("/run", methods=["POST"])
def run_attack():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data received."
            }), 400

        attack_id = int(
            data.get("attack_id")
        )

        defense_enabled = data.get(
            "defense_enabled",
            False
        )

        mode = data.get(
            "mode",
            "llm"
        )

    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid attack ID."
        }), 400


    # --------------------------------------------------------
    # Validate experiment mode
    # --------------------------------------------------------

    if mode not in ["vulnerable", "llm"]:
        return jsonify({
            "error": "Invalid experiment mode."
        }), 400


    # --------------------------------------------------------
    # Find attack
    # --------------------------------------------------------

    attack = get_attack(attack_id)

    if not attack:
        return jsonify({
            "error": "Attack not found."
        }), 404


    user_input = attack["prompt"]

    input_blocked = False
    output_blocked = False


    # ========================================================
    # VULNERABLE BASELINE
    # ========================================================

    if mode == "vulnerable":

        response = run_vulnerable_baseline(
            user_input
        )

        result = evaluate_response(
            attack=attack,
            response=response,
            defense_enabled=False,
            input_blocked=False,
            output_blocked=False,
            mode="vulnerable"
        )

        return jsonify(result)


    # ========================================================
    # LOCAL LLM
    # ========================================================

    if mode == "llm":

        # ----------------------------------------------------
        # INPUT DEFENSE
        # ----------------------------------------------------

        if defense_enabled:

            detected_patterns = detect_injection(
                user_input
            )

            if detected_patterns:

                input_blocked = True

                response = (
                    "[BLOCKED] Potential prompt injection "
                    "detected by input security filter."
                )

                result = evaluate_response(
                    attack=attack,
                    response=response,
                    defense_enabled=True,
                    input_blocked=True,
                    output_blocked=False,
                    mode="llm"
                )

                return jsonify(result)


        # ----------------------------------------------------
        # BUILD PROMPT
        # ----------------------------------------------------

        if defense_enabled:

            prompt = build_safe_prompt(
                SYSTEM_PROMPT,
                CONFIDENTIAL_DATA,
                user_input
            )

        else:

            prompt = f"""
{SYSTEM_PROMPT}

CONFIDENTIAL DATA:

{CONFIDENTIAL_DATA}

USER REQUEST:

{user_input}
"""


        # ----------------------------------------------------
        # SEND TO LOCAL LLM
        # ----------------------------------------------------

        try:

            response = ask_llm(
                prompt
            )

        except Exception as error:

            return jsonify({
                "error": (
                    "Local LLM request failed: "
                    f"{str(error)}"
                )
            }), 500


        # ----------------------------------------------------
        # OUTPUT DEFENSE
        # ----------------------------------------------------

        if defense_enabled:

            filtered_response = sanitize_output(
                response
            )

            if filtered_response != response:

                output_blocked = True

            response = filtered_response


        # ----------------------------------------------------
        # EVALUATE RESULT
        # ----------------------------------------------------

        result = evaluate_response(
            attack=attack,
            response=response,
            defense_enabled=defense_enabled,
            input_blocked=input_blocked,
            output_blocked=output_blocked,
            mode="llm"
        )

        return jsonify(result)


# ============================================================
# STATISTICS
# ============================================================

@app.route("/statistics")
def statistics():

    return jsonify(
        calculate_statistics()
    )


# ============================================================
# RESET RESULTS
# ============================================================

@app.route("/reset", methods=["POST"])
def reset_results():

    import os

    log_file = "logs/results.json"

    if os.path.exists(log_file):

        os.remove(log_file)

    return jsonify({
        "message": "Experiment results reset."
    })


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )