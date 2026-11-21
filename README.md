[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/sata333/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/sata333/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# THE WORLD TODAY — the news of 20 November 2026 in one image

Entry for the make.fun bounty **news-image-20261120** ("Sum up 20 November's
world news in one image").

`main.py` draws a newspaper front page for **Friday 20 November 2026** — a
masthead ("THE WORLD TODAY"), a date line, five headline panels with small
drawn motifs, and an "ALSO TODAY" footer strip — and writes it as a single
1024×1024 PNG.

## How it works

- Python 3.13, **standard library only** (`os`, `struct`, `zlib`), no network
  access at runtime.
- The page is rendered pixel by pixel into an in-memory framebuffer: a
  hand-coded 5×7 bitmap font provides the typography, and simple primitives
  (rectangles, Bresenham lines, circles) draw the motifs — three interlocking
  rings for the summit, scales of justice for the ICJ, a falling chart line
  for the markets, and EU/UK flags for the Brussels deal.
- The PNG is encoded directly (IHDR/IDAT/IEND with `zlib`), with pure integer
  arithmetic throughout, so the output is fully deterministic.

## Run it

```sh
python3 main.py                      # writes /output/entry.png
OUTPUT_DIR=/tmp/out python3 main.py  # writes /tmp/out/entry.png
```

## The stories shown, and their sources

Researched on 21 November 2026 from the previous day's reporting across
several independent outlets:

1. **Three powers sign a 'peace declaration'** — Trump, Xi and Putin's
   first-ever trilateral summit in Shenzhen (on the APEC sidelines) ended in a
   joint declaration: no nuclear war, more fuel supplies, UN reform, immunity
   for state officials. It never mentioned Ukraine, and European leaders
   warned against a new Yalta.
   Sources: Channel NewsAsia (Reuters/AFP copy), South China Morning Post,
   Dawn, The Japan Times.
2. **Missiles fall on NATO soil** — Russia's largest strike of November 2026
   (27 ballistic + 84 cruise missiles and 404 drones per Ukraine's Air Force;
   "110+ missiles, 400 drones" in Kyiv's summary) hit three Kyiv bridges and
   damaged embassies; two Kh-101 missiles and a drone came down in Poland,
   which PM Tusk called a deliberate provocation as NATO jets scrambled.
   Sources: ISW Russian Offensive Campaign Assessment (20 Nov 2026), CNN,
   Kyiv Independent, BBC.
3. **ICJ: Myanmar committed genocide** — the International Court of Justice
   ruled 9–6 in The Gambia's case that Myanmar's 2017 crackdown on the
   Rohingya was genocide — the first time a state has been found responsible
   at the World Court — and ordered reparations.
   Sources: Al Jazeera, Human Rights Watch, Le Monde, Channel NewsAsia.
4. **AI fever breaks — stocks tumble** — doubts over AI spending drove a
   global sell-off: the S&P 500 fell 3.7% into correction territory and the
   Nikkei 5.06%, while Anthropic shares slid a day after its record
   $81 billion IPO.
   Sources: One Turn news digest (20 Nov 2026), BBC, Reuters.
5. **UK and EU sign new deal** — the Brussels summit agreed deals on food
   trade, carbon markets and a youth mobility scheme; PM Burnham said Britain
   would explore even closer ties.
   Sources: BBC, One Turn.

Footer ("ALSO TODAY"): a Houthi missile damaged Riyadh's tallest tower
(SCMP); Ukraine hit the Crimea Bridge again (The Japan Times); the
fossil-fuel phase-out was dropped from the COP31 draft text (Dawn); NASA's
Voyager 1 reached one light-day from Earth (SCMP).

## Verification

Two consecutive runs into different output directories produce
byte-identical files:

- `entry.png`: **21,306 bytes** (limit 1 MiB), **1024×1024** px
- SHA-256: `305e962ccb77165ff000843ee67e883c8a8f24db27219a0d671611a2eefbac2e`
  (identical for both runs)

## Layout of this directory

- `main.py` — the program (the entry)
- `entry.png` — the image it produces
- `bounty.md` — the bounty brief
- `LICENSE` — license for this repository
