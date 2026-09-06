# Codebase Audit

## Executive Summary

This is a mature, feature-rich fork of Aider: an AI pair-programming CLI with Git integration, multiple model-specific edit formats, repository mapping, web scraping, voice input, OAuth onboarding, and a Streamlit GUI.

Strengths include a clear CLI entry point, understandable component boundaries, 489 test functions, deliberate confirmation around most model-proposed edits and commands, sensible repository-map caching, and no committed production credentials found.

An independent Claude Opus 5 re-audit was reconciled into this report. It confirmed the path-move finding, disproved the original wheel-content finding, and identified additional high-priority trust-boundary and data-loss issues. The most important problems are now:

1. Repository-local `.patch.conf.yml` and `.env` files cross into command execution and provider configuration without a repository trust decision.
2. A repository-local diskcache can deserialize attacker-supplied pickle data.
3. Patch-format moves can overwrite arbitrary writable paths without destination authorization.
4. Malformed whole-file and patch responses can be applied rather than rejected, risking silent data loss.
5. The GUI shares privileged mutable state between browser sessions and is not safe to expose remotely.

Additional material risks include known-vulnerable dependencies, filesystem mutation during dry-run validation, incorrect accounting after partial edit failures, OAuth and voice resource leaks, and non-hermetic CI.

Audit scope included 691 tracked files, approximately 38,281 Python lines, packaging, Docker, workflows, scripts, documentation, and the complete test tree. A temporary wheel build and `pip-audit` were performed outside the repository. The initial orb lacked pytest, but the independent re-audit created an isolated environment and ran the basic suite: 471 passed, 5 voice-device failures, 1 skipped, and 67 subtests passed in 101 seconds after ambient environment variables and Git configuration were scrubbed.

At the original audit snapshot, the fork boundary was verified as `fe4f8b58a` on
top of upstream Aider commit `5dc9490bb`. That snapshot had no fork-specific code
changes. Subsequent Patch commits changed package identity, updates, analytics,
dependency resolution, and documentation. The counts, line numbers, and scanner
results below describe the original snapshot unless a status says otherwise;
they are not a fresh audit of the current tree. Unresolved code findings still
need verification and remediation.

## Critical / High Priority Findings

No confirmed Critical issues were found.

### [High] Untrusted repository configuration reaches command execution and API routing

**Location:** `patch/main.py:43-57,360-381,464-477`; `patch/args.py:534-555`; `patch/linter.py:47-57`; `patch/run_cmd.py:62-73`

**Problem:** A repository-root `.patch.conf.yml` is loaded automatically. It can set `lint-cmd`, while `auto-lint` defaults to true, and the configured command reaches `subprocess.Popen(..., shell=True)` after an edit. A repository `.env` is also loaded with `override=True`, allowing it to replace provider endpoint environment variables. `check_config_files_for_yes()` demonstrates that repository configuration is already recognized as a trust boundary, but protects only the `yes:` key.

**Impact:** Cloning an untrusted repository and allowing Patch to edit a file can execute a command chosen by that repository. A malicious `.env` can redirect compatible model traffic, potentially disclosing API credentials and source context on the first request. The command path was independently reproduced with a marker file.

**Recommendation:** Require an explicit, persistent trust decision keyed by canonical repository path and configuration-file hash before honoring repository-local executable commands or provider/authentication settings. Alternatively, ignore dangerous keys unless `--trust-repo-config` is supplied. User-home configuration can remain trusted.

**Suggested test:** Load an untrusted repository config containing `lint-cmd` and a provider base URL; assert neither takes effect until trust is granted.

**Confidence:** High

---

### [High] Repository-local repomap cache deserializes pickle data

**Location:** `patch/repomap.py:35-43,195-260`

**Problem:** The tag cache is stored inside the repository as `.patch.tags.cache.v4` and opened with `diskcache.Cache`. Complex values are pickle-serialized. Reading a crafted value from the cache executes pickle reduction code before application-level validation. Handling catches SQLite errors but not deserialization or schema errors.

**Impact:** A malicious repository can achieve code execution when Patch reads a planted cache if it can predict the checkout's absolute path, which is used as the cache key. Paths are predictable in common Docker and CI layouts. Corrupt non-malicious caches can also crash map generation instead of becoming a cache miss.

**Evidence:** The Opus re-audit planted a malicious diskcache value and observed its payload execute during `get_tags()`. Exploitability is constrained by the absolute-path cache key but the deserialization mechanism is confirmed.

**Recommendation:** Store the cache outside the repository in a user cache directory keyed by a hash of the canonical repository path. Serialize validated primitive tag records as JSON or another non-executable format, and treat decode/schema failures as misses.

**Confidence:** High for the mechanism; Medium for arbitrary-checkout exploitability

---

### [High] Patch moves bypass destination authorization

**Location:** `patch/coders/patch_coder.py:318-351,603-627`; `patch/coders/base_coder.py:2191-2240,2269-2304`

**Problem:** `prepare_to_edit()` authorizes only `edit[0]`, the source path. A patch can independently supply `*** Move to: <destination>`. The destination is resolved and written without passing through `allowed_to_edit()`, containment checks, read-only checks, or overwrite confirmation. `abs_root_path()` also accepts absolute paths and paths resolving outside the repository.

**Impact:** A malicious or prompt-injected model response can move an authorized chat file onto any writable path, overwrite an existing file, and remove the original. This crosses the intended model-to-filesystem authorization boundary.

**Evidence:** Only the source enters `prepare_to_edit()`. Destination parents are created automatically, and existing destinations are overwritten after a warning rather than approval.

**Recommendation:** Model every action as an explicit set of affected paths. Authorize both source and destination before application. Require separate overwrite confirmation and enforce read-only policy on the destination. Preserve intentional external-path support only behind explicit authorization.

**Suggested patch:**

```python
paths = [action.path]
if action.move_path:
    paths.append(action.move_path)

if not all(self.allowed_to_edit(path) for path in paths):
    skip_action()
```

Add regression tests for absolute paths, `../` traversal, symlinks, read-only files, declined destinations, and existing targets.

**Confidence:** High

---

### [High] General edit authorization permits paths outside the project root

**Location:** `patch/coders/base_coder.py:566-574,2191-2236`; comparison implementation at `patch/commands.py:1511-1518`

**Problem:** `abs_root_path()` resolves `Path(self.root) / path` but does not enforce containment. Absolute paths discard the root component, and `../` segments resolve outside it. `allowed_to_edit()` then treats the resolved external target as an ordinary new or non-chat file. With `--yes-always`, ordinary confirmations are automatically accepted. In default Git mode, some absolute cases fail incidentally during Git path normalization, but that exception is not a security control.

**Impact:** In no-Git mode or Git mode with auto-commits disabled, model output can write complete content outside the project after an ordinary prompt or automatic `--yes-always` response. Under default auto-commit settings, relative escapes can at least create empty external files before `git add` fails. The prompt shows the model's raw relative string rather than the resolved target, making informed approval harder.

**Evidence:** The Opus audit reproduced complete writes through `../` and absolute paths in no-Git mode, and a complete relative escape in Git mode with `--no-auto-commits`.

**Recommendation:** Reject model-originated out-of-root paths unless the resolved path was explicitly supplied by the user as an editable file. At minimum, require `explicit_yes_required=True` for any external target and display the resolved absolute path. Centralize the check in `allowed_to_edit()` so all edit formats inherit it.

**Confidence:** High

---

### [High] GUI is unauthenticated, network-exposed, and shares privileged state

**Location:** `patch/main.py:233-268`; `patch/gui.py:51-89,328-369,464-495`

**Problem:** `launch_gui()` does not set Streamlit's `server.address`. Streamlit 1.55 defaults this to `None`, which is passed to Tornado and binds all interfaces. The GUI also uses process-wide `@st.cache_resource` instances for both `State` and `Coder`. These contain chat history, prompts, files, repository state, and undo state. The GUI has no application-level authentication and exposes URL fetching and repository editing.

Authoritative behavior: [Streamlit configuration default](https://github.com/streamlit/streamlit/blob/1.55.0/lib/streamlit/config.py#L1016-L1027) and [listener setup](https://github.com/streamlit/streamlit/blob/1.55.0/lib/streamlit/web/server/server.py#L194-L222).

**Impact:** Another host able to reach the machine can open the GUI, view or interfere with shared state, submit prompts, fetch internal URLs, and potentially modify the active repository. Concurrent sessions can disclose or corrupt one another's state.

**Evidence:** There is no `--server.address=127.0.0.1`, no authentication middleware, and `State` and `Coder` are globally cached resources. The web form accepts arbitrary URLs.

The independent re-audit described Streamlit's default as loopback. That conclusion was not adopted: Streamlit 1.55's source defines `server.address = None` and passes it to Tornado, whose `None` address binds available interfaces. The source links above are the controlling evidence.

**Recommendation:** Bind to loopback by default. Replace global state with `st.session_state` and avoid sharing a mutable `Coder`. If remote access is intentional, require authentication, CSRF protection, trusted-host configuration, URL-fetch restrictions, and concurrency control.

**Suggested patch:**

```python
st_args += [
    "--server.address=127.0.0.1",
    "--browser.gatherUsageStats=false",
]
```

This addresses exposure but not session isolation.

**Status:** Resolved. `launch_gui()` now passes `--server.address=127.0.0.1`,
overridable through `PATCH_GUI_ADDRESS` or `STREAMLIT_SERVER_ADDRESS` and warned
about when the address is not loopback. `State` and the `Coder` moved from
`@st.cache_resource` to `st.session_state`, and the class-level `State.keys` and
`CaptureIO.lines` became per-instance, so no state is shared between browser
sessions. `tests/browser/test_browser.py` covers the binding and the isolation.
Authentication and URL-fetch restrictions are still absent, so remote access
remains unsupported.

**Confidence:** High

---

### Retracted: wheels omit required packages and resources

**Location:** `pyproject.toml:38-42`; `patch/main.py:394`; `patch/models.py:153-158`; `patch/repomap.py:808-823`; `patch/help.py:33-115`

**Problem:** The initial audit inferred that `include = ["patch"]` excluded subpackages. Independent artifact inspection disproved that inference.

**Impact:** None. This is not a valid finding.

**Evidence:** A clean sdist and wheel contained all 81 Python modules, all 58 tree-sitter query files, model settings, model metadata, and the resource package. Setuptools' observed discovery behavior takes precedence over the original configuration-only inference.

**Recommendation:** Keep an artifact-install smoke test in CI, but do not change discovery solely for this retracted issue.

**Confidence:** High

---

### [High] WholeFileCoder writes truncated content from an unterminated fence

**Location:** `patch/coders/wholefile_coder.py:75-128`; default selection in `patch/models.py:131`

**Problem:** At end-of-input, `get_edits()` appends an edit whenever `fname` remains set, even if the closing fence was never received. `apply_edits()` then replaces the complete file with the partial accumulated response. The sibling edit-block parser rejects unclosed blocks.

**Impact:** A normally terminated but malformed or proxy-truncated model response can silently truncate a file and then be committed. The `whole` format is the default for unknown/local models, so reachability is broad.

**Evidence:** The independent audit reproduced a five-line file being replaced by the first two partial lines from an unterminated block.

**Recommendation:** In final parsing mode, reject EOF while a fence is open. Retain permissive parsing only for non-writing live-diff preview.

**Confidence:** High

---

### [High] PatchCoder accepts patches missing the terminal sentinel

**Location:** `patch/coders/patch_coder.py:229-254,395-410`

**Problem:** Validation of `*** End Patch` is commented out and the parser explicitly tolerates a missing sentinel even though the model contract requires it.

**Impact:** A truncated response can be mistaken for a complete patch and written. Patch mode is not currently a model default, which lowers likelihood but does not mitigate data loss once selected.

**Recommendation:** Require both sentinels before returning final edits. If partial parsing is needed for previews, expose a separate non-applying parser mode.

**Confidence:** High

## Medium Priority Findings

### [Medium] Known-vulnerable dependency versions are shipped

**Location:** `requirements.txt`; `requirements/common-constraints.txt`

**Problem:** Separate `pip-audit -r requirements.txt` runs reported numerous advisories. The deeper Opus run deduplicated 93 advisory IDs across 12 packages; the initial scanner presentation counted 107 records. Direct or central affected packages include GitPython 3.1.46, LiteLLM 1.82.3, requests 2.32.5, Pillow 12.1.1, and diskcache 5.6.3. Affected transitives include aiohttp, click, idna, urllib3, Pygments, soupsieve, and Starlette.

**Impact:** Vulnerable versions are definitely present, although this audit did not establish that every advisory is reachable. Dependencies handling external data warrant prompt triage.

**Evidence:** Both independent scans found vulnerable resolved packages. Exact advisory counts should not be treated as stable; package/version/advisory identity should drive remediation.

**Recommendation:** Triage by reachable feature, upgrade direct dependencies first, regenerate constraints, run the complete suite, and add an audit gate with documented expiring suppressions. Do not force incompatible transitive upgrades independently of their parent frameworks.

**Confidence:** High for versions; Medium for application-specific exploitability

---

### [Medium] Dry-run validation mutates the filesystem before authorization

**Location:** `patch/coders/base_coder.py:2296-2304`; `patch/coders/editblock_coder.py:38-74,364-383`

**Problem:** `apply_updates()` invokes `apply_edits_dry_run()` before `prepare_to_edit()`. The replacement helper executes `fname.touch()` for a proposed new file even during dry-run.

**Impact:** `--dry-run` and declined edits can leave zero-byte files. Model-controlled external paths can create filesystem entries without authorization wherever the parent is writable.

**Recommendation:** Make dry-run pure. Use in-memory empty content for proposed new files and create them only after authorization in the real write path.

**Suggested patch:**

```python
if not fname.exists() and not before_text.strip():
    content = ""
```

**Confidence:** High

---

### [Medium] Partial edit failures report and commit paths that were not changed

**Location:** `patch/coders/base_coder.py:1585-1602,2296-2336`

**Problem:** `edited` is populated from all authorized edits before application. If sequential application partially succeeds and raises, `apply_updates()` returns the precomputed full set. The caller updates bookkeeping and auto-commits that set before checking `reflected_message`.

**Impact:** Failed responses can be reported as editing every requested file. Auto-commit can include pre-existing modifications in a path Patch never changed, especially when dirty pre-commit behavior is disabled.

**Recommendation:** Validate all edits before writing where possible and return a structured result containing only successfully changed paths plus any error.

**Confidence:** High

---

### [Medium] Full-file deletion is treated as a failed edit

**Location:** `patch/coders/editblock_coder.py:41-74`; `patch/coders/udiff_coder.py:69-118`

**Problem:** A successful replacement can produce `""`, but both coders use truthiness to distinguish success from no match.

**Impact:** Deleting the final contents of a file fails. Edit-block fallback can then apply matching text to another chat file instead.

**Recommendation:** Reserve `None` for no match and accept empty strings as successful output.

**Suggested patch:**

```python
if new_content is None:
    failed.append(edit)
else:
    self.io.write_text(full_path, new_content)
```

**Confidence:** High

---

### [Medium] OAuth callback listener can survive timeout

**Location:** `patch/onboarding.py:266-336`

**Problem:** The server blocks in `httpd.handle_request()`. After the five-minute normal timeout, the main thread does not set `shutdown_server`; it only joins for one second.

**Impact:** The daemon listener can remain bound until another request arrives or the process exits, causing resource leakage and possible failure on a subsequent attempt.

**Recommendation:** Set a finite server timeout, signal shutdown in `finally`, close the server, and verify thread termination. Add timeout, interruption, and successful-shutdown tests.

**Confidence:** High

---

### [Medium] OAuth API key file may be world-readable

**Location:** `patch/onboarding.py:357-368`; `patch/main.py:369-382`

**Problem:** The OpenRouter key is appended with ordinary `open(..., "a")`. Under a common `022` umask, the directory may be `0755` and file `0644`.

**Impact:** Other local users can read a reusable API credential on multi-user systems.

**Recommendation:** Create `~/.patch` as `0700`, create the key file atomically as `0600`, and tighten existing permissions before writing.

**Confidence:** High

---

### [Medium] Voice recordings are not deleted

**Location:** `patch/voice.py:116-180`

**Problem:** A temporary WAV is never deleted when WAV is selected. Transcription errors return before cleaning either format, and `tempfile.mktemp()` separates name selection from file creation.

**Impact:** Sensitive voice recordings accumulate in the temporary directory and consume disk.

**Recommendation:** Use `TemporaryDirectory` or secure named temporary files and delete every generated file in `finally`. Test all success and failure paths.

**Confidence:** High

---

### Partially resolved: [Medium] Core network requests have no timeout

**Location:** `patch/models.py:934-983`; `patch/versioncheck.py:64-95`

**Problem:** Copilot token exchange and PyPI version checking call `requests.get()` without timeouts.

**Impact:** Network stalls can indefinitely block model requests or startup/update checks.

**Recommendation:** Use explicit connect/read timeouts and test timeout exceptions.

```python
requests.get(url, headers=headers, timeout=(5, 30))
```

**Status:** The PyPI update check now uses `timeout=3` and has regression tests.
The Copilot request still needs timeout hardening.

**Confidence:** High

---

### [Medium] Settings and command-line logging expose provider secrets

**Location:** `patch/format_settings.py:1-26`; `patch/main.py:745-751`; `patch/io.py:995-1002`; `patch/args.py:97-112,269-285`

**Problem:** `scrub_sensitive_info()` only masks the dedicated OpenAI and Anthropic key arguments. `--api-key provider=secret` and `--set-env TOKEN=secret` remain visible in `--verbose` and `/settings` output. The raw command line is also logged on every invocation. `tool_output(..., log_only=True)` still appends to `.patch.chat.history.md` before suppressing terminal output.

**Impact:** Provider credentials and arbitrary token-like environment values are written in plaintext to a project-local history file, commonly mode `0644`, and can appear in terminals or bug reports. The file is normally gitignored but is not access-controlled.

**Evidence:** The independent audit reproduced DeepSeek and arbitrary environment secrets in formatted settings and history while only the OpenAI key was masked.

**Recommendation:** Redact by argument semantics and secret-name patterns. Mask the value side of every `PROVIDER=KEY` and `VAR=value`; never persist raw command-line secret values. Apply the same scrubber to parser environment-value output.

**Confidence:** High

---

### [Medium] CI is non-hermetic and does not test the release artifact

**Location:** `pytest.ini`; `.github/workflows/ubuntu-tests.yml`; `.github/workflows/windows-tests.yml`; `tests/scrape/test_scrape.py`; `tests/basic/test_ssl_verification.py`

**Problem:** Default tests access live websites, retry external requests, load optional functionality, and install tools into the active environment. In `test_ssl_verification.py`, a `MagicMock.name.startswith("bedrock/")` result is truthy, causing a real boto3 installation under `--yes`. Browser, scraper, and help tests similarly exercise runtime installers. CI installs from source and runs inside the checkout rather than testing a built wheel.

**Impact:** Plain `pytest` can mutate a developer or CI environment, download hundreds of megabytes, and depend on PyPI, external websites, Hugging Face, and the PyTorch index. The use of `--extra-index-url` merges indexes and increases dependency-confusion exposure. CI also misses artifact-only failures.

**Recommendation:** Patch `run_install` or `check_for_dependencies` in affected tests, give mocks concrete model names, and add an autouse fixture that fails on attempted installation. Separate `unit`, `integration`, `network`, and `installer` tests, mock HTTP in unit tests, use a single intended package index for CPU wheels, and test the wheel outside the checkout.

**Status:** Help tests now mock embedding and model boundaries, and documentation
URL tests validate retained files and anchors locally. They no longer install
extras or request remote documentation. Other network/installer tests and the
missing CI artifact gate remain unresolved.

**Confidence:** High

---

### [Medium] Release workflows can publish manually selected refs without artifact gates

**Location:** `.github/workflows/release.yml`

**Problem:** Both workflows permit `workflow_dispatch` without checking for a protected release tag or environment. PyPI uses a long-lived token, and actions/tooling use mutable tags or dynamically installed versions.

**Impact:** A mistaken invocation or compromised maintainer can publish from an unintended ref or overwrite Docker `latest`.

**Recommendation:** Require a release-tag predicate, use a protected environment, adopt PyPI trusted publishing/OIDC, SHA-pin third-party actions, and publish only tested artifacts.

**Status:** The Docker release workflow was removed. The PyPI workflow still
supports manual dispatch and needs the recommended release gates. Tag-triggered
publishing has been removed; only an explicit manual dispatch can publish.

**Confidence:** Medium

---

### [Medium] PatchCoder ADD creates a placeholder and then rejects it

**Location:** `patch/coders/base_coder.py:2206-2224`; `patch/coders/patch_coder.py:550-580`

**Problem:** `allowed_to_edit()` authorizes a new file by creating it with `touch_file()`. PatchCoder then requires an ADD target not to exist and raises `ADD Error: File already exists`.

**Impact:** Every PatchCoder ADD fails, leaves an empty file, and may stage/report the path even though requested content was never written.

**Recommendation:** Separate authorization from file creation. The edit implementation should own creation after approval, or PatchCoder must recognize its own authorized zero-byte placeholder.

**Confidence:** High

---

### [Medium] File replacement is non-atomic

**Location:** `patch/io.py:478-507`

**Problem:** `write_text()` opens the destination with mode `"w"`, truncating it before the new content is completely written. Only permission errors are retried.

**Impact:** Disk exhaustion, process interruption, encoding failure, or I/O failure after truncation can leave an empty or partial file. This amplifies malformed-response failures.

**Recommendation:** Write and `fsync` a temporary file in the destination directory, preserve intended permissions where applicable, then use `os.replace()`.

**Confidence:** High

---

### [Medium] History summarization can silently discard unsummarized messages

**Location:** `patch/history.py:45-96`

**Problem:** The code finds a `split_index` for the retained tail, then separately token-limits `sized_head` into `keep`. Messages between the end of `keep` and `split_index` are neither summarized nor retained.

**Impact:** Relevant requirements or prior decisions disappear silently from the conversation, causing incorrect subsequent edits without an explicit context-limit warning.

**Evidence:** The independent probe used unique message IDs and observed only ID0 reach the summarizer while only ID5 remained; ID1–ID4 vanished.

**Recommendation:** Chunk and summarize the complete head recursively. Add a conservation test asserting every uniquely marked message is either supplied to a summarizer call or retained in the tail.

**Confidence:** High

---

### [Medium] File watcher lets any local writer initiate an LLM turn

**Location:** `patch/watch.py:80-120,205-265`; `patch/io.py:670-675`

**Problem:** With `--watch-files`, any process able to modify a watched file can add an `AI!` marker. That interrupts input and returns a generated code-edit prompt as the next user turn without confirmation. Simultaneous `AI!` and `AI?` changes are stored in a set, making selected action order nondeterministic.

**Impact:** Formatters, language servers, build tasks, or compromised dependencies can trigger API spending and model-proposed edits. Normal edit authorization still limits writes, so this is not direct arbitrary code execution.

**Recommendation:** Require confirmation before the first watcher-triggered action from an external file event, make action precedence deterministic, and document the local-writer trust assumption.

**Confidence:** High

---

### [Medium] Git exception tuple hides ordinary programming errors

**Location:** `patch/repo.py:15-36,295-318` and other `except ANY_GIT_ERROR` call sites

**Problem:** `ANY_GIT_ERROR` includes `TypeError`, `ValueError`, `AttributeError`, `AssertionError`, `IndexError`, and `BufferError` in addition to Git and OS failures.

**Impact:** Programming defects inside broad Git operations are converted into ordinary “Unable to commit” failures, suppressing tracebacks and allowing execution to continue with state different from what callers expect.

**Recommendation:** Restrict the tuple to documented Git exceptions and narrowly justified OS errors. Catch data-shape errors only at specific parsing boundaries.

**Confidence:** High

---

### Resolved: [Medium] Optional extras cannot resolve on supported Python 3.10

**Location:** `pyproject.toml:20,32-36`; `requirements/requirements-dev.txt:151`; `requirements/requirements-help.txt:209`; `requirements/requirements-browser.txt:65`; `requirements/python-compat.in`

**Problem:** The project supports Python 3.10, and the base dependency metadata retains a Python-version split for NumPy. Compiled extras pin `numpy==2.4.3` unconditionally, which is incompatible with Python 3.10.

**Impact:** Installing `patch-code[dev]`, `[help]`, or `[browser]` fails on a declared supported Python version. CI installs the base project rather than extras and misses this.

**Recommendation:** Preserve environment markers when compiling each extra and add resolver/install jobs for every supported Python version and extra combination.

**Status:** Resolved. The locks are now compiled with universal resolution from Python 3.10 so markers are preserved, and `tests/basic/test_requirements.py` checks pin consistency across base and extras for every supported Python version on Linux and Windows.

**Confidence:** High

---

### Resolved: [Medium] Manual untagged builds derived an inconsistent project version

**Location:** `pyproject.toml:44-49`; `patch/__init__.py:3-18`; `.github/workflows/release.yml:3-34`

**Problem:** This fork's remote has no tags. `setuptools_scm` therefore derives a version such as `0.1.dev...`, while runtime `safe_version` is `0.86.3.dev`. Tag-triggered builds would derive from a newly pushed tag, but the release workflow also allows manual dispatch from an untagged ref.

**Impact:** A manual release can upload metadata that sorts below real Aider releases and disagrees with runtime version reporting.

**Recommendation:** Require a valid release tag and fail the build if SCM-derived and declared safe versions are inconsistent. A fallback version alone is weaker than preventing untagged publication.

**Status:** Runtime and package metadata now read the same explicit version from
`patch/__init__.py`, starting at Patch `0.1.0`. SCM-derived versions and the inherited
version floor have been removed. Manual publishing still requires version and
artifact review; this resolves version disagreement, not release authorization.

**Confidence:** High for manual untagged builds

---

### [Medium] Published metadata exposes the full exact dependency lock

**Location:** `pyproject.toml:29-36`; `requirements.txt`

**Problem:** The distribution's runtime dependencies are read directly from an application lock containing roughly 110 exact `==` pins, including the complete transitive closure. This lock is useful for CI and containers but unusually restrictive as published package metadata.

**Impact:** Installing `patch-code` into a shared Python environment can force exact versions of unrelated transitive packages, create resolver conflicts with other applications, and require a Patch release for every transitive security update.

**Recommendation:** Keep a reproducible lock for tested application environments, but publish reviewed direct dependencies with compatible lower/upper bounds. Validate both the locked standalone installation and resolution alongside representative packages.

**Confidence:** High

## Low Priority Findings

### [Low] Docker runtime user can modify installed application code

**Location:** `docker/Dockerfile:21-24,50-51,74-75`

**Problem:** `/venv` is owned by `appuser`, and site-packages are made world-writable.

**Impact:** Commands can persistently alter installed code in a long-lived container. This is not privilege escalation, but it weakens integrity.

**Recommendation:** Keep `/venv` root-owned and read-only; make only explicit runtime and cache directories writable. Avoid recursive `777`.

**Confidence:** High

---

### Resolved: [Low] Contributor documentation contradicts current configuration

**Location:** `CONTRIBUTING.md:156-170,187-216`; `pyproject.toml:20`; `pytest.ini:4-8`

**Problem:** The guide says Python 3.9–3.12 while metadata targets 3.10–3.14, says tests live in `patch/tests`, and references requirement files at incorrect paths.

**Impact:** Contributors can use unsupported versions, run invalid commands, or place tests incorrectly.

**Recommendation:** Update and periodically validate documentation against project metadata, workflows, and actual paths.

**Status:** Resolved. The guide now states Python 3.10–3.14, points at the `tests` directory, and uses the real `requirements/` paths.

**Confidence:** High

---

### Resolved by removal: [Low] Documentation-site dependencies were not locked

**Status:** The inherited website and Jekyll tooling have been removed. Patch
ships a small Markdown set in `patch/docs/`; no Ruby or website build remains.

**Confidence:** High

---

### [Low] Public export metadata and debug leftovers are defective

**Location:** `patch/coders/__init__.py:18-34`; `patch/analytics.py:208`; `patch/coders/base_coder.py:2280-2281`; `patch/coders/editblock_coder.py:183-187`; `patch/scrape.py:257`; `patch/models.py:967-976`; `patch/commands.py:1278-1314`

**Problem:** `patch.coders.__all__` contains class objects instead of strings, so `from patch.coders import *` raises `TypeError`. Additional confirmed leftovers include unconditional debug output on PostHog errors, a `dump(edits)` path for a filename literally named `python`, unreachable fuzzy matching after a bare return, only the first image being removed during HTML slimming, a Copilot error containing a token prefix and complete response body, and `/paste` path/temporary-directory cleanup defects.

**Impact:** These produce broken wildcard import behavior, noisy or potentially sensitive diagnostics, dead maintenance surface, incomplete HTML cleanup, and leaked pasted-image temporary files. None rises to the severity of the findings above in the normal threat model.

**Recommendation:** Store names in `__all__`, remove debug branches and unreachable matching, iterate over all images, avoid including any credential fragment or unbounded provider body in errors, sanitize pasted-image basenames, and clean temporary directories deterministically.

**Confidence:** High

---

### Resolved: [Low] Fork identity and self-update behavior were upstream-owned

**Location:** `pyproject.toml:2-27`; `patch/versioncheck.py:15-35,78`; `patch/analytics.py`; `README.md:31-39`

**Problem:** Before the rename, the fork still identified as the upstream `aider-chat` package, linked to the upstream homepage, checked/upgraded from upstream PyPI or GitHub, reported opted-in analytics to the upstream project, and displayed upstream badges.

**Impact:** A fork user accepting an upgrade replaces this checkout's distribution with upstream Aider. If the fork is published, it collides with upstream package and console-script identity. Analytics and project provenance may be surprising despite the README's fork notice.

**Recommendation:** Either explicitly remain an unmodified downstream mirror and document upstream update/telemetry behavior, or choose distinct package/update/analytics identity before distributing fork-specific builds.

**Status:** Resolved. Package identity, the homepage, and the version-check/upgrade path are Patch-owned, and the upstream analytics keys have been removed. Patch now ships no analytics destination: the PostHog client is only constructed when the user supplies `--analytics-posthog-project-api-key`, and the opt-in prompt is never shown otherwise.

**Confidence:** High

---

### Resolved: [Low] Current pre-commit lint job has a deterministic failure

**Location:** `patch/onboarding.py:229-233`; `.pre-commit-config.yaml:11-15`; `.flake8`

**Problem:** `do_GET()` declares `nonlocal server_error` but never assigns it. Flake8 reports F824, which is not ignored by project configuration.

**Impact:** The pre-commit workflow fails on the current tree, reducing confidence in CI and obscuring future lint regressions.

**Evidence:** The independent audit ran Flake8 and observed exactly this one fatal warning.

**Recommendation:** Remove the unused `server_error` declaration from `do_GET`; retain it only in the closure that assigns it.

**Status:** Resolved. The unused declaration was removed and `flake8` now reports no findings on the tree.

**Confidence:** High

---

### Resolved: [Low] Analytics exception autocapture bypasses normal field redaction

**Location:** `patch/analytics.py:106,135-160,196-204`

**Problem:** The opted-in PostHog client enables automatic exception capture. That channel can include exception messages and stack traces with local paths or provider response text, independently of the explicit model-name redaction used for normal events.

**Impact:** Opted-in users can transmit more diagnostic context to the upstream analytics project than the normal event schema suggests. No API-key exfiltration through this path was reproduced, so this is a privacy-hardening issue rather than a confirmed credential leak.

**Recommendation:** Disable automatic exception capture or sanitize exception type/message/frames through a dedicated allowlist before transmission. Document retained fields and consent behavior.

**Status:** Resolved. `enable_exception_autocapture` is now `False`, so only the explicitly redacted events in `event()` are transmitted, and the client is only constructed at all when the user configures their own PostHog project.

**Confidence:** Medium

## Architecture Assessment

The primary flow is:

```text
patch.main (CLI/config)
    -> Model/LiteLLM -> provider API
    -> Coder (context, authorization, edit orchestration, commit/lint/test)
        -> edit-format subclasses -> filesystem
        -> RepoMap/Git -> cache/ranking
```

Major boundaries are generally sensible. The primary weakness is that `Coder` combines policy and execution: authorization, dry-run validation, mutation, commit bookkeeping, linting, and error reflection use loosely structured tuples and sets. This directly enables the destination-authorization and partial-result bugs.

The highest-value structural improvement is a small explicit edit-plan boundary:

- Parsed action with source, destination, operation, and expected content.
- Validation and authorization of every affected path.
- Pure calculation or preflight.
- Application returning actual changed paths and failures.
- Commit and lint driven only by the application result.

The GUI must be treated as a separate trust boundary. A process-global mutable CLI object is unsuitable for a multi-session server.

Repository configuration and caches form a second architectural trust boundary that is currently implicit. Data committed by a repository must not be treated like trusted user-home configuration or deserialized executable state. Move these decisions into an explicit repository-trust service used by configuration, environment loading, caches, watcher automation, and future executable hooks.

Typing is sparse and there is no mypy or Pyright configuration. Blanket annotation is unnecessary, but edit-plan/results, OAuth responses, model metadata, and configuration boundaries would benefit from dataclasses, `TypedDict`, or discriminated unions.

## Security Assessment

The main exploitable concerns are the patch move authorization bypass and remotely reachable GUI. OAuth file permissions are a confirmed local credential risk.

No committed real API keys, passwords, or privileged tokens were found. Analytics identifiers appear to be ingestion identifiers, not privileged secrets.

Potential false positives explicitly rejected:

- `/run`, `/git`, editor, and notification subprocesses are deliberate local-user features.
- Model-suggested shell commands retain explicit confirmation.
- CLI `/web` is not SSRF against its local user; it becomes SSRF when exposed through an unauthenticated remote GUI.
- OAuth PKCE binds the authorization code despite the absence of traditional `state`; takeover was not demonstrated.
- `search_replace.py` is active through `udiff_coder.py`.

## Testing Assessment

The suite is broad and generally uses concrete assertions. Highest-value missing tests are:

1. Patch move authorization and traversal/symlink cases.
2. GUI session isolation and loopback binding.
3. Wheel installation outside the checkout.
4. Dry-run and declined-edit filesystem invariants.
5. Accurate changed paths after partial application.
6. Whole-file deletion in both affected formats.
7. OAuth shutdown and key permissions.
8. Voice cleanup on every exit path.
9. HTTP timeout behavior.
10. Concurrent GUI requests if multi-user operation remains supported.

The Opus audit ran `tests/basic` in an isolated venv. With `NO_COLOR`, API-key variables, and ambient Git configuration scrubbed, the result was 471 passed, 5 failures caused by the orb having no audio device, 1 skipped, and 67 passing subtests. Without scrubbing, 45 tests failed because host environment and global Git commit-signing configuration leaked into tests. Add an autouse isolation fixture and skip or mock voice-device tests when no device exists.

Excluding the five improperly device-dependent voice tests produced 468 passed, 1 skipped, and 67 passing subtests. Coverage over that basic suite was 57% (10,882 statements, 4,716 missed). Security-critical `patch_coder.py` had 11% coverage and no tests instantiate PatchCoder; `gui.py` had 0%. Scrape, browser, help, version-check, watcher, onboarding, and other optional boundaries also have low coverage. Add parser fuzzing or property tests for editblock, unified-diff, and patch input.

Coverage gaps newly confirmed by the re-audit include no complete PatchCoder ADD round trip, no required end-sentinel tests, no WholeFileCoder unterminated-fence test, weak history conservation assertions, and no repository-config trust tests. `benchmark/test_benchmark.py` is excluded by `pytest.ini` and CI.

Live network and installer tests should not run in the default unit suite.

## Performance Assessment

No confirmed major algorithmic performance defect was found. `RepoMap` performs expensive parsing, graph construction, and PageRank, but uses disk caching and token budgets. Full tracked-file scans and NetworkX ranking are reasonable profiling targets for very large repositories, not rewrite candidates without measurements.

Other profiling targets are large retained command output, unbounded scraped page content, and concurrent use of a globally shared GUI coder. Correctness and trust-boundary fixes should come first.

## Dependency Assessment

Dependency management is centralized through input files and generated constraints. Main issues are vulnerable resolved versions, no automated vulnerability gate, no hashes, unconstrained Docker-only dependencies, dynamic release tooling, and a large production dependency set. No package was proven unused; Flake8, Pandoc support, NetworkX, and tree-sitter integrations all serve runtime features.

The original audit observed host-dependent lock drift, including a missing
Watchdog pin and accelerator dependencies. Universal resolution from Python 3.10
has since replaced host-only compilation; regression tests check pin consistency
on Linux and Windows across Python 3.10–3.14. The website-only development
dependencies were removed with the site and the locks regenerated. These changes
do not establish that the earlier vulnerability advisories have all been resolved;
a fresh security scan is still required.

## Dead / Duplicate Code

- **Low, High confidence:** `patch/coders/editblock_func_coder.py:9-85` is unreachable in normal operation: its constructor always raises and it is absent from the coder registry. Its prompt module appears removable.
- **Low, High confidence:** `patch/coders/wholefile_func_coder.py:8-50` also always raises and is not registered. Its prompt module appears removable.
- **Low, Medium confidence:** `patch/coders/single_wholefile_func_coder.py` is commented out of `patch/coders/__init__.py:16,28` and has no code callers. Check unofficial external imports before removal.
- **Low, High confidence:** `replace_closest_edit_distance` in `patch/coders/editblock_coder.py:296` has only one call, located after an unconditional return at line 183.
- **Low, High confidence:** `GUI.search`, `do_settings_tab`, `do_add_image`, `do_run_shell`, and `do_git` in `patch/gui.py` have definitions but no callers in the repository.
- `patch/coders/search_replace.py` remains active through five imports in `udiff_coder.py`, but its standalone benchmarking harness and several helpers have no external references and can be split or removed after focused tests.
- The two tree-sitter query trees are intentional compatibility fallback data, not accidental duplication.

## Recommended Refactoring Plan

### Phase 1 — Immediate fixes

- Gate repository-local config and environment settings in `main.py` and `args.py` behind an explicit trust decision.
- Move and safely serialize the tag cache in `repomap.py`.
- Root-contain model-originated paths in `base_coder.py` while preserving explicitly user-added external files; separately authorize patch destinations in `patch_coder.py`.
- Redact `--api-key`, `--set-env`, environment-derived secrets, and raw command lines before writing settings or history.
- Bind and isolate the GUI in `main.py` and `gui.py`.
- Reject unterminated whole-file blocks and patches before mutation.
- Upgrade reachable vulnerable dependencies and regenerate constraints.

### Phase 2 — Reliability

- Make dry-runs pure in `editblock_coder.py`.
- Repair PatchCoder ADD authorization/creation ordering.
- Make `io.write_text` atomic.
- Fix empty-result handling in `editblock_coder.py` and `udiff_coder.py`.
- Return actual application results from `base_coder.py`.
- Preserve all history messages through summarization.
- Fix OAuth lifecycle and permissions in `onboarding.py`.
- Guarantee cleanup in `voice.py`.
- Add HTTP timeouts in `models.py` and `versioncheck.py`.
- Prevent installation from tests, isolate ambient environment/Git configuration, and split network/installer tests from deterministic tests.

### Phase 3 — Architecture

- Add a small typed edit-action/result contract shared by `base_coder.py` and edit subclasses.
- Centralize affected-path authorization without changing supported file semantics.
- Define per-session GUI ownership and concurrency rules.
- Separate model parsing, policy validation, and filesystem execution.
- Define repository-supplied configuration/cache/watch inputs as an explicit untrusted boundary.

### Phase 4 — Cleanup

- Remove confirmed deprecated coders and prompts after compatibility review.
- Completed: correct contributor paths, Python matrix, and optional-extra guidance.
- Completed: establish distinct Patch package/update identity and remove default analytics collection.
- Completed: remove the inherited site and Jekyll dependencies; package Markdown help instead.
- Add targeted typing at external-data and edit-application boundaries.
- Tighten Docker permissions.

## Top 10 Actions

Ranked by impact and likelihood relative to effort:

| Rank | Action | Impact | Likelihood | Effort |
|---:|---|---|---|---|
| 1 | Gate repository `.patch.conf.yml` and `.env` behind trust | High | High | Medium |
| 2 | Root-contain model-originated edits and authorize PatchCoder destinations | High | High | Low–Medium |
| 3 | Move repomap cache out of repositories and remove pickle | High | Medium | Medium |
| 4 | Reject truncated model edits and make writes atomic | High | Medium | Medium |
| 5 | Redact all CLI/settings secrets before history logging | High | Medium | Low |
| 6 | Stop tests installing packages; isolate environment and Git config | Medium | High | Low–Medium |
| 7 | Upgrade/audit dependencies and separate published ranges from locks | High | Medium | Medium |
| 8 | Preserve every message during history summarization | Medium | High at context limits | Medium |
| 9 | Bind/isolate the GUI and secure OAuth local state | High | Medium | Medium |
| 10 | Repair PatchCoder ADD, dry-run, partial-result, and empty-file behavior | High | Medium | Medium |
