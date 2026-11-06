# Bandit parity rules

This folder ports five Bandit checks to Opengrep: B602, B307, B301, B506,
and B324. The reference is Bandit 1.9.4 with default settings on its complete
`examples/` corpus at tag `1.9.4`; the target engine is Opengrep v1.33.1.

## Work in progress

Rules and colocated Python fixtures will live in `rules/<ID>.yaml` and
`rules/<ID>.py`. `compare.py` will run both tools and report matched, missing,
and extra findings per check, comparing check ID, corpus-relative path, and
start line with multiplicity.

The initial scaffold does not yet contain rules or establish finding parity.
Rerun instructions and verified results will be added after integration.

The comparison covers only these five checks on the pinned example corpus.
It does not claim equivalence on arbitrary Python programs, other checks, or
finding messages, severity, confidence, columns, or end positions.
