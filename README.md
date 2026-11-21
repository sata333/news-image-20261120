# The World Today — 20 November 2026 Strategic Intelligence Infographic

An entry for the make.fun bounty
[“Sum up 20 November's world news in one image”](https://make.fun/bounty/news-image-20261120).

`main.py` is a self-contained Python 3.13 program (standard library only, no
network, zero external dependencies) that renders a high-definition, publication-grade
strategic intelligence dashboard of the day's global developments.
It writes the output to `/output/entry.png` (or `$OUTPUT_DIR/entry.png`).
Running it any number of times produces bit-exact, identical bytes.

```sh
python3 main.py
```

- **Output format**: 1024×1024 PNG (2x supersampled downsampled RGB raster)
- **File size**: ~63.8 KiB (well under the 1 MiB limit)
- **Determinism**: 100% bit-exact across independent runs (SHA-256 verified)

---

## Strategic Stories Covered (Friday, 20 November 2026)

1. **Shenzhen Tri-Summit (Geopolitics)**
   - Trump, Xi Jinping, and Vladimir Putin hold an unprecedented three-way summit in Shenzhen, China.
   - A joint peace declaration is issued; notably, concrete agreements on a Ukraine ceasefire are omitted.
2. **ICJ Rohingya Genocide Ruling (International Law)**
   - The UN International Court of Justice (ICJ) at The Hague finds Myanmar guilty of genocide against Rohingya Muslims.
   - Marks the court's first formal genocide ruling against a state entity.
3. **Kyiv Diplomatic & Cathedral Strikes (Security / War)**
   - A major Russian missile barrage strikes central Kyiv, damaging multiple European diplomatic embassies and the historic St. Volodymyr's Cathedral.
   - Simultaneously, Ukraine carries out strikes on the Crimea Bridge for the third time in a week.
4. **Global Tech & AI Market Rout (Finance & Technology)**
   - Global equity markets tumble sharply as post-IPO valuation doubts surrounding Anthropic's record Nasdaq debut trigger a sector-wide tech selloff.
   - Tokyo's Nikkei 225 drops 4.8%; Nasdaq and European bourses suffer heavy losses.
5. **Voyager 1 Crosses 1 Light-Day Threshold (Deep Space Exploration)**
   - NASA confirms Voyager 1 is now one light-day (25.9 billion km) from Earth.
   - Radio telemetry takes a full 24 hours to reach mission controllers, marking an interstellar exploration milestone.
6. **COP31 Fossil Language Controversy & Global Health (Climate & Health)**
   - Draft treaty text at COP31 drops explicit commitments to phase out fossil fuels under oil-producer pressure.
   - Kenya officially discharges its last Ebola patient, declaring an end to the outbreak.
   - Riyadh air defenses successfully intercept a missile targeting a commercial tower.

---

## Visual Architecture & Technical Implementation

- **Low-res Mercator Dot-Matrix Map**: 60×18 procedural matrix visualizing the globe with illuminated hotspots and coordinates.
- **Micro Ticker Strip**: Real-time financial indicators (Nikkei, Nasdaq, Brent, Gold, Defense readiness).
- **Custom 5×7 Scalable Typography Engine**: Full ASCII support with proportional spacing, line wrapping, and dynamic centering.
- **Vector-Level Drawing Primitives**: Supersampled anti-aliased circles, thick vectors, filled polygons, and card panels.

## License

MIT — see `LICENSE`.
