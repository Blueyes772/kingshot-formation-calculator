# ⚔️ KingShot Formation Calculator

AI-powered troop formation calculator for the mobile game KingShot by Century Games.

## Features

- **Troop Input** — Enter your troops by type (Infantry, Cavalry, Archer) and level (I–VIII)
- **Hero Selection** — Pick heroes for all 3 slots (Infantry hero, Cavalry hero, Archer hero)
- **AI Analysis** — Powered by DeepSeek (via OpenRouter), with free model fallback
- **Formation Guide** — Built-in knowledge for every scenario:
  - General Rally / Open Field (50/20/30)
  - vs Heavy Cavalry Enemy (60/20/20)
  - Garrison Defense (70/30/0 — no archers)
  - Bear Hunt (10/10/80 — max archers)
  - Counter Archer-Heavy Enemy (30/50/20)
  - Castle Battle Attack (50/20/30)
  - Castle Battle Defense (60/20/20)
- **Combat Mechanics** — Rock/paper/scissors (Inf > Cav > Arch > Inf), attack order, cavalry bypass

## Hero Database

Includes all known heroes from GitHub repos and community guides:
- Infantry: Helga, Eric, Alcar, Gordon, Saul, Howard, Fahd, Quinn
- Cavalry: Jabel, Jaeger, Thrud, Hilde, Marlin, Petra, Rosa, Diana
- Archer: Chenko, Yeonwoo, Amane, Margot, Amadeus, Valora, Zoe

## Sources

- [ko9ma7/KingShot-Helper](https://github.com/ko9ma7/KingShot-Helper) — formation ratios and hero data
- [smoothbread-dev/kingshot-bear-trap-troop-formation-calculator](https://github.com/smoothbread-dev/kingshot-bear-trap-troop-formation-calculator) — hero ratio logic
- [texnottexas/kingshot-bear-hunt](https://github.com/texnottexas/kingshot-bear-hunt) — hero tier list and damage math
- [genie49/kingshot-bear-guide](https://github.com/genie49/kingshot-bear-guide) — hero selection guide
- [Ahmedio65/ks-formation-hero](https://github.com/Ahmedio65/ks-formation-hero) — hero name list
- Falcon OP YouTube guide — combat mechanics and formation ratios

## License

MIT

## Live Demo

**GitHub Pages:** https://blueyes772.github.io/kingshot-formation-calculator/

The standalone version (`index.html`) calls the AI directly from the browser — no backend needed. Works on GitHub Pages, mobile, or any static host.

## Files

- `index.html` — Browser-only version (calls OpenRouter API directly, works on GitHub Pages)
- `formation-calc.html` — Full version (requires Python backend for AI analysis)
- `formation-server.py` — Python backend server for the full version
