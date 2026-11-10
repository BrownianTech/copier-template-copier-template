# Review plan

From a review of the repo and the fork's branches on 2026-11-10. The aim: keep
`copier update` diffs small for generated projects, with or without Renovate,
while a new project still starts with current dependencies.

## The rule behind most of this

A project with Renovate only gets `copier update` conflicts when the template
is behind what the project's own Renovate has already merged. Checked by hand:
a project generated at v0.27.0 with uv moved on to 0.13.9 conflicts in both
workflows when updated to v0.28.0 (uv 0.13.7). The same update is clean when
the project is at or behind the template's value.

So anything a generated project automerges, this repo must automerge at least
as fast, with the same settings on both sides.

## 1. Land what is in flight

- [ ] Merge #183 (`feat/task-apt-install`)
- [ ] Force push the rebased `feat/ci-skip-installed-tools` and
      `feat/gitlab-prebuilt-ci-image` to the fork (`--force-with-lease`), then
      open them in that order. Each has one rewritten commit the fork doesn't
      have (`93409e0`, `f2effc0`)
- [ ] Fix #178 by hand: it has conflict markers committed in
      `.github/workflows/pre-commit.yml` (`# v7` against `# v7.0.1`, take the
      latter)
- [ ] Merge #180 and #177
- [ ] Open `ci/cancel-superseded-pr-runs` upstream (fork only so far)
- [ ] Decide what to do with `feat/enable-actions-lockfile`
- [ ] Fast-forward local and fork `main` to upstream
- [x] Cache renders in the tests: `test/cache-sub-project-renders`, pushed to
      the fork, PR not opened yet (suite 36.7s to 22.6s on `main`)

## 2. Close the lag sources

- [ ] Dockerfile digest (prebuilt image branch): `debian:trixie-slim@sha256:…`
      is pinned, but digest updates under `meta_template/**` wait for review
      here while generated projects automerge them. Port the rolling-tag
      automerge rule from `feat/gitlab-pin-image-digests`
- [ ] CI images (`debian:trixie-slim`, `docker:dind`, `docker:cli`) are
      tag-only in the template, so a project's Renovate pins them on day one
      and diverges. Needs decision 1
- [ ] Automerge minor and patch action updates for `meta_template/**`, gated
      by the tests. Neither side automerges them today
- [ ] Scheduled job: render GitHub and GitLab projects, run Renovate with
      `--platform=local --dry-run=lookup`, fail if it proposes anything
- [ ] Self-hosting drift test: render with this repo's answers and assert the
      workflows, task files and `CONTRIBUTING.md` match the root. They match
      today, nothing enforces it

## 3. Fix the first hour of a new project

Found by running the documented steps in a fresh GitHub render:

- [ ] No `uv.lock` is generated, so `task dev-setup:venv:ci` fails and the
      first CI run fails until one is committed
- [ ] No pre-commit config: `task lint` fails, and once `task dev-setup` has
      installed the hook, prek rejects commits. The generated README and
      CONTRIBUTING never mention the pre-commit template
- [ ] Fix both with `_message_after_copy` and a "First steps" section in
      `CONTRIBUTING.md.tmpl`: run `uv lock`, apply the pre-commit template, set
      `GITLAB_TOKEN` or run `gh actions-lock` where relevant

## 4. Shrink routine diffs

- [ ] `_skip_if_exists` for starter files users rewrite: the example tests,
      `models.py`, `extensions/README.md`
- [ ] `tests/conftest.py`: users must edit
      `mock_answers_required_without_defaults` in a file the template also
      owns. Move the user-owned part to its own skip-if-exists file
- [ ] Move the root-only additions in `tests/helpers.py` to a separate module,
      for the same reason
- [ ] Upstream the root `ruff.toml` test ignores the template lacks (`D101`,
      `D102`, `PLR0917`)

## 5. Bugs and polish

- [ ] Generated GitLab CI file fails `yamllint --strict`: five lines over 120
      characters, four of them Renovate annotation comments (184 to 213).
      Checked with this repo's `.yamllint.yaml`; a GitLab project's config from
      the pre-commit template may differ
- [ ] Generated `models.py` (`include_pydantic_validation=true`) fails
      `ruff check` (3 errors) and `ruff format --check`
- [ ] GitHub: a push to `main` runs the test matrix twice, from `test.yml` and
      from `release.yml` calling it. Needs decision 3
- [ ] GitLab: each release appears to run three pipelines (merge, release
      commit, tag) and no job is tag-specific. Read from the rules, not seen on
      a live run
- [ ] Workflows trigger only on `main`, while the semantic-release config
      accepts `main|master`
- [ ] No validator on `output_template_name` or `template_dir`, which feed
      paths and the package name
- [ ] Typos: "checking your the template", "it's usage", "custon",
      "approprately", "mounded", "commmands"

## 6. Tests

The suite mostly asserts that a string or key is present in a render. It
doesn't check that the output is valid, lints cleanly or runs.

- [ ] Lint rendered output across an answer matrix: yamllint, ruff, shellcheck
      and the `check-jsonschema` schemas. The hooks only see this repo's files
      and skip every `.tmpl`. Expect the two bugs in section 5 as the first
      failures
- [ ] Pairwise flag combinations feeding that test, e.g. prebuilt image with
      non-root and no Docker
- [ ] Update path: GitLab and the beta flags, opting in and out of a flag via
      `copier update`, and the Renovate cases (project level with the template
      is clean, project ahead is a known conflict)
- [ ] Stop working around the onboarding gaps: `test_dev_setup` writes a sample
      pre-commit config and `test_dev_setup_venv_ci` runs `uv lock` first. Test
      the documented first steps once section 3 lands
- [ ] Run the generated project's own tests, and the inner-template copy, for
      more than default answers: square brackets, both extensions, GitLab
- [ ] Opt-in marker that runs the install scripts in `debian:trixie-slim` and
      builds the Dockerfile, on a schedule as it needs network. Also catches a
      rotated apt key before users do
- [ ] Assert `RENOVATE_ANNOTATION_REGEX` in `tests/helpers.py` matches the
      match string in `renovate.json`
- [ ] Readable ids for parametrised cases, in place of `sub_project0-True`

## 7. Supply chain

The stack's approach holds up: no script is fetched and run at job time, and
the script comments say what each check does and doesn't prove.

Weak points in it:

- [ ] Committed apt keys can go stale. A rotation breaks every generated
      project's CI until a template release, and Renovate doesn't track keys
      (covered by the scheduled install test in section 6)
- [ ] uv's checksum comes from the same release as the archive, so it catches
      corruption, not a malicious publisher. Stronger: the official uv image
      pinned by version and digest, which Renovate maintains natively and only
      changes with the version. Blocked on a custom manager for `image:` lines
      in the `.tmpl`
- [ ] Task on GitHub: `go-task/task` releases aren't immutable, and the
      workflow gets Task through `setup-task`. Check whether that action
      verifies a checksum

Further recommendations, most valuable first:

- [ ] Release-age cooldown: uv, copier, Task and lock file maintenance
      automerge as soon as a release appears. Set `minimumReleaseAge` (three
      days is common) in `renovate.json` and `renovate.json.tmpl`, identical on
      both sides
- [ ] Least privilege for releases: both release jobs run
      `uv sync --group dev`, putting pytest, plumbum and prek next to a token
      with write access. Give python-semantic-release its own dependency group
- [ ] Protect this template's tags: projects pin `_commit` to a tag, and
      templates with extensions run under `--trust`. Enable immutable releases
      and a tag ruleset upstream (current settings not checked, the token got
      a 403)
- [ ] `persist-credentials: false` on the checkout in `test.yml`, as the tests
      run third-party code
- [ ] Pass `github.sha` through `env` in the release workflow, not inline in
      `run:`
- [ ] Add zizmor as a hook, and to the rendered-output lint in section 6
- [ ] Document GitLab's protected container tags for the prebuilt image's
      `latest`, as anyone who can run a pipeline can push to the registry

Unpinned Debian archive packages (curl, git, ca-certificates) stay as they
are: old versions vanish, so pinning them would only break builds.

## 8. Ideas, lower priority

- [ ] A `template:update` helper that resolves version-only conflicts by
      keeping the newer value

## Decisions

1. **Rolling image digests.** Pinning on both sides means a template release
   for every `trixie-slim` and `dind` refresh, and a conflict whenever a
   project takes a template update late. The alternative: leave rolling tags
   unpinned and set `pinDigests: false` for those images in the generated
   `renovate.json`. Recommended, as the job installs unpinned Debian packages
   anyway. It cuts against the rule that downstream Renovate stays in charge of
   template files. The digest-pinned uv image in section 7 would sidestep this
   for the tests job's base image.
2. **README under `_skip_if_exists`.** Fewest diffs, but users stop receiving
   README improvements. Recommended: leave it merged as today.
3. **Duplicate GitHub test runs.** Dropping `push` from `test.yml` fixes it but
   stops the README badge tracking `main`. Triggering the release from
   `workflow_run` keeps the badge, with a less obvious workflow. Leaning
   `workflow_run`.
