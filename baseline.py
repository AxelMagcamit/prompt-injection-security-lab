"""
Controlled vulnerable baseline for the Prompt Injection Security Lab.

This is intentionally vulnerable and exists only as a
controlled experimental baseline.

It uses the same synthetic secret as the evaluator.
"""

from config import FAKE_SECRET


def run_vulnerable_baseline(
    attack_prompt: str
) -> str:

    suspicious_terms = [

        "ignore previous",
        "ignore all previous",
        "reveal",
        "disclose",
        "show the secret",
        "print the secret",
        "tell me the secret",
        "what is the secret",
        "confidential",
        "system prompt",
        "developer message",
        "previous instructions",
        "override",
        "bypass",
        "instructions",

    ]


    prompt = attack_prompt.lower()


    detected = any(

        term in prompt

        for term in suspicious_terms

    )


    if detected:

        return (

            "Laboratory vulnerable "
            "baseline response:\n\n"

            "CONFIDENTIAL TEST VALUE: "

            f"{FAKE_SECRET}"

        )


    return (

        "Laboratory vulnerable "
        "baseline response:\n\n"

        "No confidential information "
        "was disclosed."

    )