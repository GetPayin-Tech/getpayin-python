# Releasing

This package is published to [PyPI](https://pypi.org/p/getpayin) automatically via
GitHub Actions using **Trusted Publishing** (OIDC) — there are no API tokens or
secrets stored in the repo. See `.github/workflows/release.yml`.

## One-time PyPI setup (do this once, before the first release)

Because `getpayin` does not exist on PyPI yet, register it as a **pending
publisher** so the very first automated upload can create it:

1. Sign in at <https://pypi.org> with the account that should own the project.
2. Go to **Your account → Publishing** (<https://pypi.org/manage/account/publishing/>).
3. Under **Add a new pending publisher**, fill in exactly:
   - **PyPI Project Name:** `getpayin`
   - **Owner:** `GetPayin-Tech`
   - **Repository name:** `getpayin-python`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
4. Save.

(Optional, recommended) In the GitHub repo, create an **Environment** named
`pypi` under *Settings → Environments* and add protection rules — e.g. require a
reviewer before the publish job runs.

After the first successful publish, the pending publisher becomes a regular
trusted publisher automatically.

## Cutting a release

1. Bump the version in **both** places (they must match):
   - `pyproject.toml` → `[project].version`
   - `src/getpayin/_version.py` → `__version__`
2. Update `CHANGELOG.md`.
3. Commit to `main`.
4. Tag and push — the tag drives the release:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

   The `release.yml` workflow verifies the tag matches the package version,
   builds the sdist + wheel, runs `twine check`, and publishes to PyPI.

> The current version is `0.2.0`; the latest existing tag is `v0.1.0`, so the
> next release tag is `v0.2.0`.

## Testing against TestPyPI (optional)

To rehearse without touching real PyPI, register a matching pending publisher on
<https://test.pypi.org> and add a `repository-url` to the publish step:

```yaml
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
```

## Manual fallback (no CI)

```bash
python -m pip install --upgrade build twine
python -m build
twine check dist/*
twine upload dist/*   # requires a PyPI API token in ~/.pypirc
```
