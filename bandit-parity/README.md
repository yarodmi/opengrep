# Bandit parity rules

This folder ports five Bandit checks to Opengrep: B602, B307, B301, B506,
and B324. The reference is Bandit 1.9.4 with default settings on its complete
`examples/` corpus at tag `1.9.4`; the target engine is Opengrep v1.33.1.

| Check | Behavior |
| --- | --- |
| B602 | Subprocess calls with `shell=True` |
| B307 | `eval` calls |
| B301 | Pickle deserialization |
| B506 | Unsafe YAML loading |
| B324 | Weak hash use |

Rule files and colocated fixtures use `rules/<ID>.yaml` and `rules/<ID>.py`.
`compare.py` reports matched, missing, and extra findings by check ID,
corpus-relative path, and finding start line, preserving duplicate findings.
Messages, severity, confidence, columns, and end positions are not compared.

## Local setup (Linux x86_64)

Use existing pinned tools if available. Otherwise, these commands keep all
downloads and Python packages under `~/opengrep-bandit/`, without a global
install or source build. They require Python 3 with venv support, Git, and an
authenticated GitHub CLI. Use a fresh directory; do not overwrite existing work.

```sh
set -e
export WORK="$HOME/opengrep-bandit"
mkdir -p "$WORK"
gh release download v1.33.1 --repo opengrep/opengrep \
  --pattern opengrep_manylinux_x86 --pattern opengrep_manylinux_x86.cert \
  --pattern opengrep_manylinux_x86.sig --dir "$WORK"
gh release download v3.1.4 --repo sigstore/cosign \
  --pattern cosign-linux-amd64 --pattern cosign-linux-amd64.sigstore.json \
  --dir "$WORK"
chmod u+x "$WORK/cosign-linux-amd64"
"$WORK/cosign-linux-amd64" verify-blob \
  --bundle "$WORK/cosign-linux-amd64.sigstore.json" \
  --certificate-identity keyless@projectsigstore.iam.gserviceaccount.com \
  --certificate-oidc-issuer https://accounts.google.com \
  "$WORK/cosign-linux-amd64"
"$WORK/cosign-linux-amd64" verify-blob \
  --certificate "$WORK/opengrep_manylinux_x86.cert" \
  --signature "$WORK/opengrep_manylinux_x86.sig" \
  --certificate-identity 'https://github.com/opengrep/opengrep/.github/workflows/rolling-release.yml@refs/heads/release-v1.33.1' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  "$WORK/opengrep_manylinux_x86"
chmod u+x "$WORK/opengrep_manylinux_x86"
git clone --depth 1 --branch 1.9.4 https://github.com/PyCQA/bandit.git \
  "$WORK/bandit-src"
python3 -m venv "$WORK/.venv"
"$WORK/.venv/bin/pip" install 'bandit==1.9.4'
export OPENGREP="$WORK/opengrep_manylinux_x86"
"$OPENGREP" --version
"$WORK/.venv/bin/bandit" --version
sha256sum "$OPENGREP"
git -C "$WORK/bandit-src" rev-parse HEAD
```

Both signature checks must print `Verified OK` before using Opengrep.
Cosign is bootstrapped from its official HTTPS release and checks its own
Sigstore bundle. The commands retain certificate identity and transparency
verification. Stop if verification fails.

Expected Opengrep version: `1.33.1`; SHA256:
`46e8133cc490f9f50518061590ce2f6be5a08afaeda034471c0ceda4b3899808`.
Expected Bandit version: `1.9.4`; source commit at tag `1.9.4`:
`92ae8b82fb422a639f0ed8d99e96cea769594e08`.

## Rerun

From the repository root, with `OPENGREP` set to the pinned executable:

```sh
export OPENGREP="${OPENGREP:-$HOME/opengrep-bandit/opengrep_manylinux_x86}"
"$OPENGREP" --test bandit-parity/rules
```

The comparison command and integrated results will be added after the
comparison script and rules arrive. No parity result is claimed yet.

## Coverage limits

The complete pinned corpus is authoritative, including nonfindings. Default
Bandit reports syntax errors for `new_candidates-none.py`, `nonsense.py`, and
`nonsense2.py`; do not edit or exclude those files. Compare observed findings
and report parser errors separately, including any Opengrep extras in files
Bandit skipped. Unexpected operational or parsing errors block validation.

These results cover only the five checks on this corpus, not arbitrary Python
programs or other Bandit checks. Passing fixtures alone is not parity evidence.
