# test-simply

Playwright scraper for Simply Wall St — extracts management and shareholder data for SGX-listed companies.

## Setup

```bash
uv pip install -e .
```

Requires Chrome installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`.

## Project structure

```
src/scraper/
├── simply.py              # main scraper & orchestration
└── utils/
    ├── checkpoint.py      # save/load/clear run state
    ├── human.py           # human-like mouse, keyboard, scroll simulation
    ├── io.py              # file writing, filename sanitization
    └── parser.py          # HTML extraction (React Query state, Redux state)
```

## Usage

Edit the `companies` list and account credentials in the `__main__` block of `simply.py`, then run:

```bash
uv run -m scraper.simply
```

Checkpoints are saved to `data/checkpoint/remaining_companies.json` so interrupted runs resume where they left off. Output is written to:

```
data/management/         # management member data
data/shareholders/by_type/      # ownership breakdown by type
data/shareholders/top_shareholders/ # top shareholders ranked
```
