# Agentic Development Harness — a case study

A self-directed system that lets AI agents **plan, build, review, and validate their own changes** to a real Android game (built, pre-launch) — with a human on every step that can't be undone.

Built solo, from first principles, over ~4 months. It's built to *ship*, not to gold-plate: every gate below exists so I can move fast without shipping something broken. This repo documents the **architecture**; the product source stays private.

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

## The manager — and where I sit
Above the five stages sits one **orchestration layer** that I direct: it plans each unit of work, routes it to the right role and model, and holds the system's state between steps. I designed the roles, the gates, and the routing; the harness runs them. I'm not outside the loop supervising a black box — I'm the system's judgment and authority, and the manager is the layer that extends that across many parallel agents.

## Per-role model routing
Not every stage needs the same brain. Reasoning-heavy judgment (Strategy, Critic, Evaluation) runs on a stronger, colder model; routine execution runs on a faster one. A **model-gate** refuses to let a judgment role run on an under-powered model.

## The oracle — correctness you can *prove*
The money question for any agentic system: how do you know it didn't break something?

- **Differential oracle** *(designed, pre-launch)* — the core logic already exists **twice**: a reference build and a performance-critical native port that's authoritative on device. Two independent implementations of the same rules make each one the other's oracle, which is what catches a "fixed one side, not the other" divergence. Wiring them into an automated gate is pre-launch work — the technique itself is built and runnable in [evals-differential-oracle](https://github.com/egnaro9/evals-differential-oracle).
- **Logic invariants** — core rules (e.g. *"a reward fires only from a direct user action, never as a downstream side effect"*) are enforced as **property-based tests over the native engine** — the implementation that's authoritative on device. 51 tests (16 of them property-based, over random inputs), device-free, one command, last run green. The rule itself is implemented on both sides and proven on hardware; the automated enforcement lives on the engine.
- **On-device validation** — adb-driven tests confirm behavior on real hardware, not just in a mock.

## The evidence trail — every close leaves proof
Speed only counts if you can show the work held. Every closed unit of work leaves a durable, machine-checkable proof:

- **NO-PROOF-NO-CLOSE.** A work item cannot close until an automated check confirms its proof exists on disk. The loop physically cannot skip it.
- **Provenance-bound proof.** On-device validation screenshots are sanitized (sensitive regions blacked out), and provenance manifests bind each image to the exact git SHA, screen dimensions, and redaction method that produced it — so an artifact traces back to the commit it proves.
- **Human-gated checkpoints.** Each checkpoint records scoped git staging (explicit paths only), a commit/SHA trail across the repos it touches, an artifact-registry audit, and an explicit operator approval.
- **Periodic self-eval.** An independent evaluation role scores the system's health with a delta versus the prior period and a failure taxonomy; regressions feed a failure registry that drives fixes.

## The autonomy ladder
Trust is earned in named levels, **L0–L4**. The rule: higher levels remove *clicks* (auto-launching the safe steps), never *gates*.

```
L0 Manual → L1 Assisted → L2 Hands-off relay (current) → L3 Auto-advance launches → L4 Lights-out
```

A human still approves anything irreversible or outward-facing. **Reliability earns launch-automation; it never earns gate-removal.**

## Safety gates
Every irreversible action — device deploys, git commits/pushes — waits for an explicit human approval phrase. The agent can't self-grant. The gates are *structural* (a deny-floor, a cold critic, device validation, an approval-gated checkpoint), not just good intentions.

## Operating record (spring–summer 2026)
From the on-disk archive: ~200 completed work-arcs · ~190 human-gated checkpoints · 74 independent cold-critic reviews · 13 periodic self-evaluations · a ~200-file sanitized proof archive with ~90 provenance manifests · a failure registry with per-item root-cause fixes.

## Verifiable outcomes (all public)
The same operator + harness, on public work you can check:
- An arcade game — **Tap Dodge Rush**, under SeraphLight Studios — shipped end-to-end to [Google Play](https://play.google.com/store/apps/details?id=com.seraphlight.tapdodgerush).
- A one-character fix **merged upstream into TeaVM** (the Java-to-JavaScript compiler), closing a long-dormant issue.
- A **live public model-drift board** grading 16 LLMs daily on a frozen, deterministically-graded suite — no LLM-as-judge, so a score change is real.
- Ten public repos, including a [differential-oracle testing project](https://github.com/egnaro9/evals-differential-oracle) and a Model Context Protocol server built from the spec.

## What I take from it
- Evals and oracles are the hard, valuable part; getting a demo to work *once* is not the job.
- Cold, independent review beats a model grading its own homework.
- Autonomy is safe when the gates sit on the irreversible steps — not on the competence.
- Build to ship: the gates exist so speed doesn't cost you correctness.
