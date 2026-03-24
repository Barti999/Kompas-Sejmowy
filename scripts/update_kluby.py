"""
update_kluby.py
---------------
Pobiera listę klubów i kół z Sejm API i porównuje ze stanem lokalnym.
Wykrywa: nowe koła, rozwiązane koła, zmiany nazwy i liczby członków.
"""

import requests
from utils import (
    load_json, save_json, load_meta, save_meta,
    now_iso, today_iso, append_changelog
)
from detektory import DETEKTORY_KLUBOW

API_BASE    = "https://api.sejm.gov.pl/sejm"
KADENCJA    = "term10"
PLIK_KLUBOW = "kluby.json"


def pobierz_kluby_z_api():
    url = f"{API_BASE}/{KADENCJA}/clubs"
    print(f"  Pobieram: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    print("\n=== Aktualizacja klubów ===")

    lokalne = load_json(PLIK_KLUBOW)
    if lokalne is None:
        print("  Brak lokalnego pliku — pierwsze uruchomienie.")
        lokalne = []

    slownik_lokalny = {k["id"]: k for k in lokalne}
    api_lista = pobierz_kluby_z_api()
    slownik_api = {k["id"]: k for k in api_lista}

    zmiany_changelog = []
    licznik = {"nowe": 0, "zmienione": 0, "rozwiazane": 0, "bez_zmian": 0}

    # Nowe i zmienione
    for klub_id, klub_api in slownik_api.items():
        if klub_id not in slownik_lokalny:
            slownik_lokalny[klub_id] = dict(klub_api)
            slownik_lokalny[klub_id]["_od"] = today_iso()
            slownik_lokalny[klub_id]["_aktywny"] = True
            licznik["nowe"] += 1
            zmiany_changelog.append({
                "typ":      "nowe_kolo",
                "klub_id":  klub_id,
                "nazwa":    klub_api.get("name", ""),
            })
            print(f"  [NOWE]     {klub_api.get('name')} (id: {klub_id})")
            continue

        rekord = slownik_lokalny[klub_id]
        zmieniony = False

        for detektor in DETEKTORY_KLUBOW:
            pole = detektor["pole"]
            stara = rekord.get(pole)
            nowa  = klub_api.get(pole)
            if stara != nowa:
                print(f"  [ZMIANA]   {klub_api.get('name')} — {pole}: {stara} → {nowa}")
                rekord[pole] = nowa
                zmiany_changelog.append({
                    "typ":      detektor["typ_zmiany"],
                    "klub_id":  klub_id,
                    "nazwa":    klub_api.get("name", ""),
                    "z":        str(stara),
                    "na":       str(nowa),
                })
                zmieniony = True

        if zmieniony:
            licznik["zmienione"] += 1
        else:
            licznik["bez_zmian"] += 1

    # Rozwiązane koła (były lokalnie, nie ma w API)
    for klub_id in list(slownik_lokalny.keys()):
        if klub_id not in slownik_api:
            if slownik_lokalny[klub_id].get("_aktywny", True):
                slownik_lokalny[klub_id]["_aktywny"] = False
                slownik_lokalny[klub_id]["_do"] = today_iso()
                licznik["rozwiazane"] += 1
                zmiany_changelog.append({
                    "typ":     "rozwiazane_kolo",
                    "klub_id": klub_id,
                    "nazwa":   slownik_lokalny[klub_id].get("name", ""),
                })
                print(f"  [ROZWIĄZ.] {slownik_lokalny[klub_id].get('name')} (id: {klub_id})")

    if any(v > 0 for k, v in licznik.items() if k != "bez_zmian"):
        save_json(PLIK_KLUBOW, list(slownik_lokalny.values()))
        append_changelog(zmiany_changelog)
        meta = load_meta()
        meta["kluby"] = {"ostatnia_aktualizacja": now_iso()}
        save_meta(meta)
    else:
        print("  Brak zmian — plik nie został nadpisany.")

    print(f"\n  Podsumowanie: {licznik['nowe']} nowych, {licznik['zmienione']} zmienionych, "
          f"{licznik['rozwiazane']} rozwiązanych, {licznik['bez_zmian']} bez zmian.")
    print("=== Gotowe ===\n")


if __name__ == "__main__":
    main()
