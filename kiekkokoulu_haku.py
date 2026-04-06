import json, os
from datetime import datetime
from espn_api.hockey import League

LEAGUE_ID = 69315
SEASON = 2025
ESPN_S2 = "AEBk0e7t%2BLmvm2UXCfHIgCdghatBiuTXYOoseVzgeuyoXFLy4Xbk3otFtA%2B2cSj3pTQyENK8ZKvv%2BODsFqlXfrN8Qp0o6vt9b6hy9%2FYbf%2F3cQ1hI49Gpo5BvoP3kiBF3d0dtPuSTitcidWiOcp99IKRtxr4U%2FO4hHlR4K%2BqZVMHAiLIDAok27QVWKuDQegS6vjKCdjy8793x8ZvWXKYL7YLcXqKN1faJWs4wPPeyZ2QMaSnI5D80c5OZmcQBAfLM9UyWj6B9G2d6BpIqmTDHeNgr"
SWID = "{ECB71F9E-711C-48E2-B71F-9E711C78E256}"

TIEDOSTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pisteet.json")
KAUSI_TIEDOSTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kausi_pisteet.json")

def laske_pisteet(stats):
    g   = stats.get('G', 0)
    a   = stats.get('A', 0)
    pm  = stats.get('+/-', 0)
    pim = stats.get('PIM', 0)
    ppg = stats.get('PPG', 0)
    shg = stats.get('SHG', 0)
    sv  = stats.get('SV', 0)
    so  = stats.get('SO', 0)
    w   = stats.get('W', 0)
    return round(g*3 + a*2 + pm*1 + pim*(-1) + ppg*1 + shg*2 + (sv//5)*1 + so*5 + w*3, 1)

def lataa_kausi_data():
    if os.path.exists(KAUSI_TIEDOSTO):
        with open(KAUSI_TIEDOSTO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"kuukaudet": [], "joukkueet": {}}

def paivita_kausi(kausi_data, taman_kuun_pisteet, kuukausi):
    if kuukausi in kausi_data["kuukaudet"]:
        print(f"Kuukausi {kuukausi} jo laskettu, ohitetaan kausipisteiden paivitys.")
        return kausi_data
    kausi_data["kuukaudet"].append(kuukausi)
    for espn_id, pisteet in taman_kuun_pisteet.items():
        if espn_id not in kausi_data["joukkueet"]:
            kausi_data["joukkueet"][espn_id] = {"kausi_yht": 0, "kuukaudet": {}}
        kausi_data["joukkueet"][espn_id]["kausi_yht"] += pisteet
        kausi_data["joukkueet"][espn_id]["kuukaudet"][kuukausi] = pisteet
    with open(KAUSI_TIEDOSTO, "w", encoding="utf-8") as f:
        json.dump(kausi_data, f, ensure_ascii=False, indent=2)
    print(f"Kausipisteet paivitetty: {KAUSI_TIEDOSTO}")
    return kausi_data

# --- Haku ---
league = League(league_id=LEAGUE_ID, year=SEASON, espn_s2=ESPN_S2, swid=SWID)
print(f"Liiga: {league.settings.name}, {len(league.teams)} joukkuetta")

now = datetime.now()
month_key = f"{now.year}-{str(now.month).zfill(2)}"

joukkueet = []
taman_kuun_pisteet = {}

for team in league.teams:
    stats = team.stats or {}
    pisteet = laske_pisteet(stats)
    manager = team.owners[0].get('displayName', '') if team.owners else team.team_name

    taman_kuun_pisteet[str(team.team_id)] = pisteet

    j = {
        "espnTeamId": str(team.team_id),
        "espnTeamName": team.team_name,
        "managerName": manager,
        "seasonPts": pisteet,
        "monthPts": {month_key: pisteet},
        "wins": int(stats.get('W', 0)),
        "losses": int(stats.get('GA', 0)),
        "standing": getattr(team, 'standing', 0),
    }
    joukkueet.append(j)
    print(f"OK {team.team_name} ({manager}) - {pisteet} pistetta")

# Tallenna kuukausitiedot
data = {
    "paivitetty": now.isoformat(),
    "liiga": league.settings.name,
    "kausi": SEASON,
    "joukkueet": joukkueet,
}
with open(TIEDOSTO, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Tallennettu: {TIEDOSTO}")

# Päivitä kauden kumulatiiviset pisteet
kausi_data = lataa_kausi_data()
paivita_kausi(kausi_data, taman_kuun_pisteet, month_key)
# GitHub auto-push
import subprocess

subprocess.run(["git", "-C", r"C:\Users\eerot\Kiekkokoulu", "add", "."], check=True)
subprocess.run(["git", "-C", r"C:\Users\eerot\Kiekkokoulu", "commit", "-m", f"Pisteet paivitetty {now.strftime('%d.%m.%Y')}"], check=True)
subprocess.run(["git", "-C", r"C:\Users\eerot\Kiekkokoulu", "push"], check=True)
print("GitHub paivitetty!")