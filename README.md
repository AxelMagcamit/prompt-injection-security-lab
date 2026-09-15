# Prompt Injection Security Lab

A local cybersecurity laboratory for studying prompt injection attacks, LLM behavior, and defensive techniques in a controlled environment.

---

## Project Overview

The Prompt Injection Security Lab is a local experimental environment designed to demonstrate how prompt injection attacks can affect Large Language Model (LLM) applications.

The project allows different prompt injection techniques to be tested against:

1. A controlled vulnerable baseline
2. A local LLM without defenses
3. A local LLM with security defenses enabled

The laboratory uses a synthetic secret instead of real credentials or sensitive information. This allows prompt injection experiments to be performed safely in a controlled environment.


### Dashboard

![Prompt Injection Security Lab Dashboard](docs/dashboard.png)

---

## Why I Built This

I built this side project to better understand prompt injection and how LLM applications can be manipulated through specially crafted instructions.

Instead of only reading about prompt injection, I wanted to create a small laboratory where I could actually execute different attack scenarios, observe the model's behavior, and test defensive techniques.

The project uses a controlled synthetic secret so that the experiments can be performed safely without using real credentials or sensitive information.

---

## How the Lab Works

The laboratory follows this general flow:

```text
Attack Scenario
       |
       v
+----------------------+
| Experiment Mode      |
+----------------------+
       |
       +--------------------+
       |                    |
       v                    v
Vulnerable Baseline     Local LLM
                            |
                            v
                    Input Detection
                            |
                            v
                    Safe Prompt Builder
                            |
                            v
                       Local LLM
                            |
                            v
                    Output Sanitization
                            |
                            v
                       Evaluation
                            |
                            v
                    Experiment Logging