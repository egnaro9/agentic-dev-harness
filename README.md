# Agentic Development Harness — a case study

A self-directed system that lets AI agents **plan, build, review, and validate their own changes** to a shipping product — with a human on every step that can't be undone.

Built solo, from first principles, over ~4 months. This repo documents the **architecture**; the product source stays private.

> Built by **Erik Hill** — agentic systems engineer.
> Portfolio → https://egnaro9.github.io · LinkedIn → https://linkedin.com/in/erik-hill-98895575

---

## The problem
Coding agents are easy to demo and hard to *trust*. The moment they touch a real codebase — deploys, commits, user-facing changes — you need what any production system needs: review, tests, gates, and a way to catch your own regressions. This harness is my answer.

## The loop
Work moves through five stages, each handing off automatically:

```
Strategy → Execution → Critic → Evaluation → Ops
```

- **Strategy** plans the change.
- **Execution** builds it.
- **Critic** reviews it in *cold context* — a fresh model with no memory of building it — so it catches what the builder rationalized away.
- **Evaluation** runs the checks.
- **Ops** ships it, behind a human gate.

Hooks arm the next stage on their own, so the loop advances without a human babysitting each handoff.

## Per-role model routing
Not every stage needs the same brain. Reasoning-heavy judgment (Strategy, Critic, Evaluation) runs on a stronger, colder model; routine execution runs on a faster one. A **model-gate** refuses to let a judgment role run on an under-powered model.

## The oracle — correctness you can *prove*
The money question for any agentic system: how do you know it didn't break something?

- **Differential oracle** — the same core logic runs in **two independent implementations** (a React build and a native engine). Invariant tests hold both to the same rules; a divergence in one is caught by the other.
- **Logic invariants** — core rules (e.g. *"a reward is granted only by a direct player action — never by a cascade or a power-up"*) are enforced as tests, in **both** implementations.
- **On-device validation** — adb-driven tests confirm behavior on real hardware, not just in a mock.

## The autonomy ladder
Trust is earned in named levels, **L0–L4**. The rule: higher levels remove *clicks* (auto-launching the safe steps), never *gates*.

```
L0 Manual → L1 Assisted → L2 Hands-off relay (current) → L3 Auto-advance launches → L4 Lights-out
```

A human still approves anything irreversible or outward-facing. **Reliability earns launch-automation; it never earns gate-removal.**

## Safety gates
Every irreversible action — device deploys, git commits/pushes — waits for an explicit human approval phrase. The agent can't self-grant. The gates are *structural* (a deny-floor, a cold critic, device validation, an approval-gated checkpoint), not just good intentions.

## What I take from it
- Evals and oracles are the hard, valuable part; getting a demo to work *once* is not the job.
- Cold, independent review beats a model grading its own homework.
- Autonomy is safe when the gates sit on the irreversible steps — not on the competence.
