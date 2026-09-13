# COS40005 Testing Tool

`shapeup-scan` clones or copies a project, detects the app type, runs quality checks (tests, ESLint, jscpd, Playwright, and more), then writes a downloadable `.log` report.

## Setup (once)

```bash
cd COS40005-Testing-Tool
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium
```

## One command: run every demo project and generate reports

```bash
shapeup-scan demo
```

That scans all bundled test projects and writes logs to `reports/`:

- `reports/healthy-app.log`
- `reports/messy-app.log`
- `reports/broken-ui-app.log`
- `reports/all-projects.log` (combined file you can present or download)

## Scan one project

Local folder:

```bash
shapeup-scan scan ./examples/healthy-app
```

GitHub repo:

```bash
shapeup-scan scan https://github.com/some-user/some-repo.git
```

Custom report path:

```bash
shapeup-scan scan ./examples/messy-app -o ./reports/messy-app.log
```

## Demo projects

| Project | What it shows |
| --- | --- |
| `examples/healthy-app` | Has lint, test, and build scripts. Clean code. Page should pass Playwright. |
| `examples/messy-app` | Missing lint/test/build. Duplicated code for jscpd. Unused helpers for ESLint/Knip. |
| `examples/broken-ui-app` | Scripts look fine, but the page throws console/page errors for Playwright. |
