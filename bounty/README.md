# Reserve Protocol bug-bounty review, local run

Target: the Reserve Protocol bug bounty on Cantina (up to $10M critical, $100k high,
$5k medium, $1k low). In scope: the core protocol at release **4.2.0** (commit
`3ad40fa`) and tag **3.4.0-rc1**, the listed collateral plugins, `Governance.sol`,
`DutchTrade`/`GnosisTrade`, the 3.4.0 spell, plus the Folio (DTF) repo and trusted
fillers. The Folio and trusted-fillers code was already reviewed in depth (four
passes) with nothing to submit; the core protocol and plugins are the open work.

## 1. One-time setup (about 10 minutes, mostly compiling)

```bash
bash bounty/setup-local.sh ~/bounty
```

This clones the code at the in-scope versions, converts every prior audit to text
under `~/bounty/coreaud` (reviewers must drop anything already reported there),
installs dependencies and compiles both repos.

## 2. Run the review

Open Claude Code in this repository (`claude`), switch the model to Fable 5.1
(`/model`), and paste:

> ultracode. Run `bounty/wf-reserve-core-shard.js` as four parallel workflows with
> `scriptPath`, each with args `{"scratch": "/Users/<you>/bounty", "shard": <name>,
> "units": <list>}`:
> - `core-1`: `["rtoken","basket","backing","revenue"]`
> - `core-2`: `["strsr","trading","main-auth","fixed-math"]`
> - `plugins-1`: `["asset-base","aave","compound","curve-yearn"]`
> - `plugins-2`: `["morpho","eth-lsd","stable-yield","governance-spell"]`
>
> When they finish, read the four `core-report-*.md` files in the workspace and
> summarize surviving findings with their proof-of-concept status.

Each unit gets two reviewers with different lenses (accounting/state and
integration/actors). Every candidate is then checked by three independent agents
(already in an audit? does the code path really work? in scope and material?) and
only findings that pass all three get a Hardhat regression test. Reports land in
`~/bounty/core-report-<shard>.md`.

## 3. Submitting

Reproduce any surviving finding yourself before submitting. Cantina requires a $100 deposit per
submission, wants enough information to reproduce and fix the issue (a proof-of-concept
is preferred, and is our bar), rates severity as impact x likelihood, requires the issue
to be previously unknown and non-public, and lists every prior audit report as known
issues.
Do not commit findings or test files to a public repository before the report is
accepted.

## Notes

- The reviewers run with full tool access and execute the repos' install scripts
  and tests. These are reputable repositories, but keep wallet keys and other
  secrets off the machine (or run in a separate macOS user or a container).
- `wf-reserve-core-shard.js` assumes the workspace layout the setup script creates:
  `protocol-3ad40fa`, `protocol-3.4.0`, `coreaud` under the `scratch` directory.
