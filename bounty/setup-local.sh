#!/usr/bin/env bash
# Local setup for the Reserve Protocol bug-bounty review (macOS or Linux).
# Usage: bash bounty/setup-local.sh [workspace-dir]   (default: ~/bounty)
#
# Clones the in-scope code at the exact in-scope versions, extracts the prior
# audit reports to text (the "known issues" list), installs dependencies and
# compiles, so that reviewers and proof-of-concept tests can run locally.
set -euo pipefail

W="${1:-$HOME/bounty}"
mkdir -p "$W" && cd "$W"
echo "Workspace: $W"

# --- tools -------------------------------------------------------------------
command -v node >/dev/null || { echo "Node.js 18+ is required (https://nodejs.org)"; exit 1; }
if ! command -v forge >/dev/null; then
  curl -L https://foundry.paradigm.xyz | bash
  "$HOME/.foundry/bin/foundryup"
fi
export PATH="$HOME/.foundry/bin:$PATH"
if ! command -v pdftotext >/dev/null; then
  if command -v brew >/dev/null; then brew install poppler; else echo "Install poppler (pdftotext) and re-run"; exit 1; fi
fi
corepack enable   # provides the Yarn 4 and pnpm versions the repos pin

# --- code at the in-scope versions -----------------------------------------
# Core protocol: release 4.2.0 (commit 3ad40fa) and tag 3.4.0-rc1 are in scope.
[ -d protocol ] || git clone https://github.com/reserve-protocol/protocol.git
git -C protocol fetch origin 3ad40fa2c79482b73e9dbd7f54c66298da6cdb4a
git -C protocol fetch origin tag 3.4.0-rc1
[ -d protocol-3ad40fa ] || git -C protocol worktree add ../protocol-3ad40fa 3ad40fa2c79482b73e9dbd7f54c66298da6cdb4a
[ -d protocol-3.4.0 ]   || git -C protocol worktree add ../protocol-3.4.0 3.4.0-rc1
# Folio (DTF) and trusted fillers, already reviewed; kept for proof-of-concept tests.
[ -d reserve-index-dtf ] || git clone https://github.com/reserve-protocol/reserve-index-dtf.git
if [ ! -d trusted-fillers ]; then
  git clone https://github.com/reserve-protocol/trusted-fillers.git
  git -C trusted-fillers checkout 303e0a56948b602365a1ed0024ed473f683aeb0f
fi

# --- prior audits -> text (the known-issues list reviewers must check) ------
mkdir -p coreaud
for f in protocol/audits/*.pdf protocol/audits/individual-plugins/*.pdf; do
  pdftotext -layout "$f" "coreaud/$(basename "$f" .pdf).txt"
done
cp protocol/audits/*.md coreaud/

# --- dependencies and compilation ------------------------------------------
( cd protocol-3ad40fa && yarn install --immutable && yarn hardhat compile )
( cd reserve-index-dtf && pnpm install --frozen-lockfile && forge build )

echo
echo "Done. Workspace: $W"
echo "Core 4.2.0:  $W/protocol-3ad40fa   (PROTO_IMPL=1 yarn hardhat test <file>)"
echo "Core 3.4.0:  $W/protocol-3.4.0"
echo "Folio:       $W/reserve-index-dtf   (forge test)"
echo "Audit text:  $W/coreaud"
