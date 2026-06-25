# IRP Tabletop Platform — local prototype

A local app that runs incident-response tabletop prep and produces evidence. This is the
**v1 prototype** (tabletop), built to run on your own machine. It is intentionally simple;
the production version will move to Lovable + Supabase later.

What works today:
- Add a **client** organization.
- Upload their **IRP/BCP (PDF)** and run an **AI gap analysis** against a best-practice
  baseline. Review/accept the gaps into a change punch-list.

Coming next: running the live exercise and generating the evidence report.

---

## Setup (one time)

You need **Python 3.10 or newer**. To check, open a terminal and run `python3 --version`.
If you don't have it, install from https://www.python.org/downloads/ (tick "Add Python to
PATH" on Windows).

Then, from this `app` folder, install the dependencies:

```
pip install -r requirements.txt
```

(If `pip` isn't found, try `python3 -m pip install -r requirements.txt`.)

## Your Anthropic API key

The AI gap analysis needs an Anthropic API key. Get one at
https://console.anthropic.com → **API keys**. You'll paste it into the app's sidebar when
it opens (it stays on your machine). Optionally, copy `.env.example` to `.env` and put your
key there so you don't have to paste it each time.

## Run it

**Mac/Linux:** double-click `run.sh`, or in a terminal from this folder:

```
./run.sh
```

**Windows:** double-click `run.bat`, or in a terminal from this folder:

```
run.bat
```

Either way, the app opens in your web browser. Use the pages in the left sidebar:
**Clients → Plan & Gaps**.

To stop the app, close the browser tab and press `Ctrl+C` in the terminal.

---

## Notes

- Your data is stored locally in `app/data/irp.db` (created on first run). Nothing is
  uploaded anywhere except the plan text sent to Anthropic for the gap analysis.
- Default AI model: `claude-opus-4-8`.
