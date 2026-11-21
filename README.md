# The World Today — 20 November 2026 in one image

An entry for the make.fun bounty
[“Sum up 20 November's world news in one image”](https://make.fun/bounty/news-image-20261120).

`main.py` is a self-contained Python 3.13 program (standard library only, no
network) that draws a newspaper front page of the day and writes it to
`/output/entry.png` (set `OUTPUT_DIR` to write elsewhere). Running it any
number of times produces exactly the same bytes.

```sh
python3 main.py
```

Output: a 1024×1024 PNG, well under the 1 MiB limit.

## The day's stories, as drawn

- **Shenzhen summit** — Trump, Xi and Putin hold their first three-way
  meeting and issue a joint peace declaration, with no mention of a
  ceasefire in Ukraine.
- **ICJ ruling** — the International Court of Justice rules Myanmar
  committed genocide against the Rohingya, its first genocide finding
  against a state.
- **Kyiv** — a Russian barrage damages embassies and St Volodymyr's
  Cathedral; Ukraine strikes the Crimea Bridge a third time in a week.
- **Markets** — global stocks tumble on AI-valuation doubts after
  Anthropic's record Nasdaq debut; the Nikkei falls 4.8%.
- **Voyager 1** — NASA's probe phones home from one light-day away; its
  signal now takes a full day to reach Earth.
- Footer: a Houthi missile damages a Riyadh tower; the COP31 draft drops
  the fossil-fuel phase-out call; Kenya discharges its last Ebola patient.

## License

MIT — see `LICENSE`.
