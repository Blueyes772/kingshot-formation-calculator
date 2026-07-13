#!/usr/bin/env python3
"""
KingShot Formation Calculator - AI-powered backend
Serves the web UI + proxies formation analysis via OpenRouter (free models first)
"""
import http.server
import socketserver
import json
import os
import urllib.request

PORT = 8766

# Load API key from UYP pipeline .env
_api_key = ""
_env_path = os.path.expanduser("~/projects/uyp-pipeline/.env")
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            if line.startswith("UYP_API_KEY" + "="):
                _api_key = line.split("=", 1)[1].strip()
                break

API_KEY = _api_key
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Free model first, DeepSeek as fallback
MODELS = [
    "deepseek/deepseek-chat",
    "openai/gpt-oss-20b:free",
]

# Hero data from GitHub repos (texnottexas guides, smoothbread-dev, genie49, Ahmedio65)
HERO_DATA = """
KNOWN KINGSOT HEROES — FULL LIST WITH ROLES AND TROOP TYPE:

INFANTRY HEROES (Slot 1):
- Helga: Lethality & Defense. Top garrison leader. Infantry focus.
- Eric: Health & Defense. Garrison infantry.
- Alcar: Damage & Infantry Defense.
- Gordon: Health (joiner). Defensive.
- Saul: Defense & Health (joiner).
- Howard: Defensive only, no rally damage.
- Fahd: Defensive only, no rally damage.
- Quinn: Defensive only, no rally damage.

CAVALRY HEROES (Slot 2):
- Jabel: Bear Hunt leader. Chance-based damage (doesn't stack well).
- Jaeger: Capacity hero. Lv3 skill gets skipped by any Lv4+ hero.
- Marlin: Chance-based damage (doesn't stack).
- Petra: Chance-based damage (doesn't stack).
- Rosa: Chance-based damage (doesn't stack).
- Diana: Niche — only useful against rallying terrors, not Bear Hunt.
- Thrud: Archer damage boost. Good in archer-heavy rallies.
- Hilde: Defense + Lethality (joiner).

ARCHER HEROES (Slot 3):
- Chenko: Lethality. Optimal ratio 1% Inf / 10% Cav / 89% Arch. Top bear hunt joiner — send first.
- Yeonwoo: Lethality. Two modes: Ratio (same as Chenko 1/10/89) or Quantity (half archers + inf/cav fill).
- Amane: Attack. Quantity mode (split archers evenly). Top bear hunt joiner.
- Margot: Attack. Top bear hunt joiner.
- Amadeus: Bear hunt joiner hero.
- Master Valora: Savage Advantage skill (+3K to +30K bonus march capacity, steps of 3K). Applies to Chenko and Lead.
- Zoe: No damage, defensive skill only.
- Seth, Forrest, Edwin, Olive: Other heroes (limited data).

BEAR HUNT TIER LIST:
- Top tier (use these): Yeonwoo, Chenko, Margot, Amane
- Avoid tier: Rosa, Marlin, Petra, Jaeger, Jabel (chance-based, doesn't stack)
- No damage: Zoe, Saul, Alcar, Eric (defensive only)
- Niche: Diana (rallying terrors only)
- Defensive only: Quinn, Howard, Gordon, Fahd

DAMAGE MATH:
- Same heroes stack additively: 4x Amane = 2.0x damage (+100%)
- Mixed stat families multiply: 2 Amane + 2 Chenko = 2.25x (+125%)
- Fully mixed: 1 Chenko + 1 Amane + 1 Margot + 1 Yeonwoo = 2.5x (+150%)
- Lethality heroes: Chenko, Yeonwoo
- Attack heroes: Amane, Margot
- Mixing Lethality + Attack families = multiplicative damage bonus

RULES:
- Only 4 joiner hero skills count per rally.
- Star level does NOT affect troop capacity.
- Only the FIRST slot hero's skill applies to the whole rally (for joiners).
- Send Chenko first if fewer than 4 Chenkos in rally.

COMBAT MECHANICS (from Falcon OP guide):
- Rock/paper/scissors: Infantry beats Cavalry > Cavalry beats Archers > Archers beat Infantry
- Combat order: Infantry attack first, then Cavalry, then Archers (fixed every round)
- Infantry = front line meat shield, absorbs all incoming damage first
- Archers = highest lethality, primary damage engine, need infantry to survive long enough
- Cavalry = disruption, percentage chance to bypass enemy infantry and strike archers directly (every round)

FORMATION GUIDE (by scenario):
1. General Rally / Open Field / Alliance Championship: 50% Inf / 20% Cav / 30% Arch
   - Variation vs heavy cavalry enemy: 60/20/20 (more infantry wall)
2. Garrison Defense (buildings/objectives): 70% Inf / 30% Cav / 0% Arch
   - Archers are terrible at defending (low defensive stats)
   - City defense softer version: 60/20/20
3. Bear Hunt (PvE): 10% Inf / 10% Cav / 80% Arch
   - Maximize archers for lethality. If can't hit 80%, max archers available, then cavalry (2nd highest lethality)
4. Counter Formations (after scouting enemy):
   - Enemy heavy infantry, low archers: attack with more archers
   - Enemy heavy cavalry: defend with more infantry
   - Enemy archer-heavy (10/10/80): counter with 30/50/20 (cavalry shreds their archers)
5. Castle Battle:
   - Attack marches: 50/20/30
   - Defense garrison: 60/20/20
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_POST(self):
        if self.path == "/api/analyze":
            content_length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(content_length))

            troops = body.get("troops", [])
            capacity = body.get("capacity", 0)
            scenario = body.get("scenario", "Rebel Bounty: Rare (Open Field)")
            hero = body.get("hero", "")
            total = sum(t.get("count", 0) for t in troops)

            # Build troop summary - order: Infantry, Cavalry, Archer
            type_order = ["infantry", "cavalry", "archer"]
            type_labels = {"infantry": "Infantry", "cavalry": "Cavalry", "archer": "Archers"}
            sorted_troops = sorted(troops, key=lambda t: type_order.index(t.get("type", "infantry")) if t.get("type") in type_order else 99)
            troop_lines = []
            for t in sorted_troops:
                ttype = t.get("type", "")
                label = type_labels.get(ttype, ttype.title())
                troop_lines.append(f"- {label}: {t.get('name', '')} x{t.get('count', 0):,}")
            troop_summary = "\n".join(troop_lines) if troop_lines else "No troops entered."

            hero_line = f"\nSELECTED MARCH LEADER HERO: {hero}\n" if hero else "\nMARCH LEADER HERO: Not selected\n"

            prompt = f"""You are a Kingshot mobile game strategy expert. A player needs a troop formation recommendation.

GAME: Kingshot by Century Games
SCENARIO: {scenario}
PLAYER'S MARCH CAPACITY: {capacity:,}
PLAYER'S TOTAL TROOPS: {total:,}
{hero_line}
PLAYER'S AVAILABLE TROOPS:
{troop_summary}

{HERO_DATA}

The standard Open Field formation ratio is 50% Infantry / 30% Archers / 20% Cavalry (infantry tanks, archers deal damage, cavalry flanks).

Analyze the player's troops and provide:
1. Can they build the full 50/30/20 march? If not, what are they short on?
2. Exactly how many of each type to send in the march (respecting what they actually have).
3. If they can't hit the ideal ratio, what's the best alternative split using what they have?
4. Which troop tiers to prioritize sending (higher tier = stronger).
5. Any troops that should stay home (surplus beyond what's needed).
6. If a hero is selected, factor in their skills and recommended troop ratios.

Keep the response concise and practical. Use a clear format:
- MARCH SETUP: [total to send] troops
- INFANTRY: send [X] (have [Y])
- CAVALRY: send [X] (have [Y])
- ARCHERS: send [X] (have [Y])
- HERO: [advice based on selected hero]
- NOTES: [any key advice]

Format numbers with commas. No markdown code blocks, just plain text."""

            payload = {
                "model": MODELS[0],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 800,
            }

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://em3enterprises.com",
                "X-Title": "KingShot Formation Calculator",
            }

            # Try free model first, fallback to DeepSeek
            for model in MODELS:
                payload["model"] = model
                req = urllib.request.Request(
                    API_URL,
                    data=json.dumps(payload).encode(),
                    headers=headers,
                )
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        result = json.loads(resp.read())
                        ai_text = result["choices"][0]["message"]["content"]
                        if ai_text:  # Got valid content
                            self._json_response({"ok": True, "analysis": ai_text, "model": model})
                            return
                        # null content — try next model
                except Exception as e:
                    err = str(e)
                    if "429" not in err and "Too Many Requests" not in err:
                        self._json_response({"ok": False, "error": err})
                        return
                    # 429 = rate limited, try next model

            self._json_response({"ok": False, "error": "All models rate-limited. Try again in a minute."})
        else:
            self.send_error(404)

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet


if __name__ == "__main__":
    print(f"KingShot Formation Calculator running on http://localhost:{PORT}")
    print(f"  Open: http://localhost:{PORT}/formation-calc.html")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.daemon_threads = True
        httpd.serve_forever()
