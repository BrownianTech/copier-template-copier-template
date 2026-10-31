# Contributing to copier-template-copier-template

## Dev setup

Prerequisites: [uv](https://docs.astral.sh/uv/) and [Task](https://taskfile.dev/).

```bash
task dev-setup
```

Run `task --list` to see all available commands.

### Optional dependencies

- [asciinema](https://docs.asciinema.org/manual/cli/quick-start/) for demo video with copiable text

## Running tests

There are two test suites:

- **`tests/`** — tests the template itself: verifies that `copier copy` and `copier update` produce the expected output.
- **`tests/sub_project/`** — tests a project generated *from* your template: verifies that the generated template works end-to-end.

Run both with:

```bash
task test
```

## Releases

Releases are automated via [python-semantic-release](https://python-semantic-release.readthedocs.io/). Preview what the next release would look like with:

```bash
task release
```

### CI setup

The release workflow uses the built-in `GITHUB_TOKEN`. If your default branch restricts pushes via [branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-a-branch-protection-rule/about-branch-protection-rules), use a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) stored as a repository secret named `GH_TOKEN` instead.

## GitHub Actions lockfile

Workflow dependencies are pinned in [`.github/workflows/actions.lock`](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles), which the `Verify lockfile` workflow checks on every push and pull request. Renovate (44.184.0 or later) regenerates it whenever it updates an action.

The lockfile is generated with the [`gh actions-lock`](https://github.com/github/gh-actions-lock) extension, which is not part of the template. Generate it once after creating the project, and again after adding a workflow or changing any `uses:` by hand:

```bash
gh extension install github/gh-actions-lock
gh actions-lock
git add .github/workflows/
```

`gh actions-lock` also rewrites digest-pinned refs in `uses:` to tags (e.g. `@<sha> # v7.0.1` to `@v7.0.1`), moving the commit into `actions.lock`, so commit the workflow changes along with it.

The template ships digest-pinned refs, so `copier update` conflicts on any `uses:` line the template changes. Keep the tag form, take the template's version, then rerun `gh actions-lock`.

Untested: enabling the [*Require actions to be pinned to a full-length commit SHA*](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/) policy for the repository may avoid these conflicts, as Renovate's docs say `gh actions-lock` then leaves digest refs in place.

CI pins the extension with `GH_ACTIONS_LOCK_VERSION` in `verify-lockfile.yml`, which Renovate keeps up to date via the `customManagers:githubActionsVersions` preset.

## Making changes

Template files live under `meta_template/`. After making changes, run `task test` to verify everything works.

To pull in upstream improvements from the meta-template:

```bash
copier update --answers-file .copier-answers.copier-template.yml
# or
task copier-template:template:update
```
