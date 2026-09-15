import json
import importlib
import os


try:
    plt = importlib.import_module("matplotlib.pyplot")
except ModuleNotFoundError:
    print(
        "ERROR: matplotlib is required to generate graphs. "
        "Install it with: python -m pip install matplotlib"
    )
    raise SystemExit(1)


LOG_FILE = "logs/results.json"
OUTPUT_DIR = "results"


# ============================================================
# LOAD EXPERIMENT DATA
# ============================================================

def load_results():

    if not os.path.exists(LOG_FILE):
        print("ERROR: results.json was not found.")
        return []

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            results = json.load(file)

        if not isinstance(results, list):
            print("ERROR: results.json does not contain a list.")
            return []

        return results

    except json.JSONDecodeError:

        print("ERROR: results.json contains invalid JSON.")
        return []


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


results = load_results()


if not results:

    print("No experiment results found.")
    exit()


print(
    f"Loaded {len(results)} experiment results."
)


# ============================================================
# GROUP RESULTS
# ============================================================

vulnerable = [
    r for r in results
    if r.get("mode") == "vulnerable"
]

llm_no_defense = [
    r for r in results
    if (
        r.get("mode") == "llm"
        and not r.get("defense_enabled", False)
    )
]

llm_defense = [
    r for r in results
    if (
        r.get("mode") == "llm"
        and r.get("defense_enabled", False)
    )
]


# ============================================================
# HELPER FUNCTION
# ============================================================

def success_rate(data):

    if not data:
        return 0

    successful = sum(
        1
        for r in data
        if r.get(
            "attack_successful",
            False
        )
    )

    return (
        successful / len(data)
    ) * 100


# ============================================================
# GRAPH 1
# ATTACK SUCCESS RATE BY CONFIGURATION
# ============================================================

configurations = [
    "Vulnerable Baseline",
    "LLM - No Defense",
    "LLM + Defense"
]

success_rates = [
    success_rate(vulnerable),
    success_rate(llm_no_defense),
    success_rate(llm_defense)
]


plt.figure(figsize=(9, 6))

bars = plt.bar(
    configurations,
    success_rates
)

plt.title(
    "Attack Success Rate by Configuration"
)

plt.ylabel(
    "Attack Success Rate (%)"
)

plt.ylim(
    0,
    100
)

plt.grid(
    axis="y",
    alpha=0.3
)


for bar, value in zip(
    bars,
    success_rates
):

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        value + 2,
        f"{value:.1f}%",
        ha="center"
    )


plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "attack_success_rate.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 2
# DEFENSE BLOCKING RATE
# ============================================================

if llm_defense:

    input_blocked = sum(
        1
        for r in llm_defense
        if r.get(
            "input_blocked",
            False
        )
    )

    blocking_rate = (
        input_blocked
        / len(llm_defense)
    ) * 100

else:

    blocking_rate = 0


plt.figure(figsize=(7, 6))

bars = plt.bar(
    ["LLM + Defense"],
    [blocking_rate]
)

plt.title(
    "Input Blocking Rate"
)

plt.ylabel(
    "Blocking Rate (%)"
)

plt.ylim(
    0,
    100
)

plt.grid(
    axis="y",
    alpha=0.3
)


plt.text(
    bars[0].get_x()
    + bars[0].get_width() / 2,
    blocking_rate + 2,
    f"{blocking_rate:.1f}%",
    ha="center"
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "defense_blocking_rate.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 3
# PER-ATTACK COMPARISON
# ============================================================

attack_ids = sorted(
    set(
        r.get("attack_id")
        for r in results
    )
)


vulnerable_rates = []
llm_no_defense_rates = []
llm_defense_rates = []


for attack_id in attack_ids:

    attack_vulnerable = [
        r for r in vulnerable
        if r.get("attack_id") == attack_id
    ]

    attack_llm_no_defense = [
        r for r in llm_no_defense
        if r.get("attack_id") == attack_id
    ]

    attack_llm_defense = [
        r for r in llm_defense
        if r.get("attack_id") == attack_id
    ]


    vulnerable_rates.append(
        success_rate(
            attack_vulnerable
        )
    )

    llm_no_defense_rates.append(
        success_rate(
            attack_llm_no_defense
        )
    )

    llm_defense_rates.append(
        success_rate(
            attack_llm_defense
        )
    )


x = range(
    len(attack_ids)
)

width = 0.25


plt.figure(
    figsize=(12, 6)
)


bars1 = plt.bar(
    [
        i - width
        for i in x
    ],
    vulnerable_rates,
    width,
    label="Vulnerable Baseline"
)


bars2 = plt.bar(
    x,
    llm_no_defense_rates,
    width,
    label="LLM - No Defense"
)


bars3 = plt.bar(
    [
        i + width
        for i in x
    ],
    llm_defense_rates,
    width,
    label="LLM + Defense"
)


plt.title(
    "Attack Success Rate by Attack Scenario"
)

plt.xlabel(
    "Attack ID"
)

plt.ylabel(
    "Attack Success Rate (%)"
)

plt.xticks(
    list(x),
    [
        f"Attack {i}"
        for i in attack_ids
    ]
)

plt.ylim(
    0,
    100
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "per_attack_results.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# SUMMARY
# ============================================================

print()
print("RESULT GRAPHS GENERATED")
print("------------------------")

print(
    "1. results/attack_success_rate.png"
)

print(
    "2. results/defense_blocking_rate.png"
)

print(
    "3. results/per_attack_results.png"
)

print()
print("Experiment summary:")
print(
    f"Total experiments: {len(results)}"
)

print(
    f"Vulnerable baseline: "
    f"{len(vulnerable)}"
)

print(
    f"LLM without defense: "
    f"{len(llm_no_defense)}"
)

print(
    f"LLM with defense: "
    f"{len(llm_defense)}"
)

print(
    f"Vulnerable baseline ASR: "
    f"{success_rate(vulnerable):.2f}%"
)

print(
    f"LLM without defense ASR: "
    f"{success_rate(llm_no_defense):.2f}%"
)

print(
    f"LLM with defense ASR: "
    f"{success_rate(llm_defense):.2f}%"
)

print(
    f"Input blocking rate: "
    f"{blocking_rate:.2f}%"
)
