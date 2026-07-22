"""Scaffoldings.

A scaffold is a strategy for wrapping a model around a task: how the prompt is
framed, how many calls are made, and how intermediate outputs feed the next
call. Comparing the *same* model under different scaffolds — or the same
scaffold across models — is the whole point of the harness.

Each scaffold's ``run`` drives a provider and returns the final answer plus a
per-call trace.
"""

from __future__ import annotations

from .providers import Provider
from .schemas import Step

# The base system prompt a scaffold layers its own instructions on top of.
_DEFAULT_SYSTEM = "You are a careful, concise assistant."


class Scaffold:
    name: str = "base"
    description: str = ""
    calls: int = 1

    def run(
        self,
        *,
        provider: Provider,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
        effort: str | None,
    ) -> tuple[str, list[Step]]:
        raise NotImplementedError

    # Small helper so subclasses stay terse.
    def _call(self, provider, model, system, messages, max_tokens, effort, label):
        c = provider.complete(
            model=model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            effort=effort,
        )
        return c, Step(
            label=label,
            input_tokens=c.input_tokens,
            output_tokens=c.output_tokens,
            output=c.text,
        )


class DirectScaffold(Scaffold):
    name = "direct"
    description = "Single call. The prompt goes straight to the model."
    calls = 1

    def run(self, *, provider, model, prompt, system, max_tokens, effort):
        sys = system or _DEFAULT_SYSTEM
        c, step = self._call(
            provider, model, sys,
            [{"role": "user", "content": prompt}],
            max_tokens, effort, "direct",
        )
        return c.text, [step]


class CoTScaffold(Scaffold):
    name = "cot"
    description = "Single call with a chain-of-thought system instruction."
    calls = 1

    def run(self, *, provider, model, prompt, system, max_tokens, effort):
        sys = (system or _DEFAULT_SYSTEM) + (
            " Work through the problem step by step before giving the final answer."
        )
        c, step = self._call(
            provider, model, sys,
            [{"role": "user", "content": prompt}],
            max_tokens, effort, "cot",
        )
        return c.text, [step]


class SelfCritiqueScaffold(Scaffold):
    name = "self_critique"
    description = (
        "Two calls: draft an answer, then critique and revise it in a fresh turn."
    )
    calls = 2

    def run(self, *, provider, model, prompt, system, max_tokens, effort):
        sys = system or _DEFAULT_SYSTEM
        draft, s1 = self._call(
            provider, model, sys,
            [{"role": "user", "content": prompt}],
            max_tokens, effort, "draft",
        )
        critique_msgs = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": draft.text},
            {
                "role": "user",
                "content": (
                    "Critique your previous answer for errors, omissions, or "
                    "unclear reasoning, then produce an improved final answer."
                ),
            },
        ]
        final, s2 = self._call(
            provider, model, sys, critique_msgs, max_tokens, effort, "revise",
        )
        return final.text, [s1, s2]


class PlanExecuteScaffold(Scaffold):
    name = "plan_execute"
    description = "Two calls: produce a short plan, then execute it."
    calls = 2

    def run(self, *, provider, model, prompt, system, max_tokens, effort):
        sys = system or _DEFAULT_SYSTEM
        plan, s1 = self._call(
            provider, model,
            sys + " Respond with a short numbered plan only — do not solve it yet.",
            [{"role": "user", "content": prompt}],
            max_tokens, effort, "plan",
        )
        exec_msgs = [
            {
                "role": "user",
                "content": (
                    f"Task:\n{prompt}\n\nPlan:\n{plan.text}\n\n"
                    "Now carry out the plan and give the final answer."
                ),
            },
        ]
        final, s2 = self._call(
            provider, model, sys, exec_msgs, max_tokens, effort, "execute",
        )
        return final.text, [s1, s2]


_SCAFFOLDS: dict[str, Scaffold] = {
    s.name: s
    for s in (
        DirectScaffold(),
        CoTScaffold(),
        SelfCritiqueScaffold(),
        PlanExecuteScaffold(),
    )
}


def get_scaffold(name: str) -> Scaffold:
    try:
        return _SCAFFOLDS[name]
    except KeyError:
        raise KeyError(f"unknown scaffold: {name!r}") from None


def all_scaffolds() -> list[Scaffold]:
    return list(_SCAFFOLDS.values())
