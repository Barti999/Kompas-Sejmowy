"""
update_glosowania.py
--------------------
Pobiera PEŁNE głosowania z indywidualnymi głosami każdego posła.
Naprawiona wersja – zaczyna od posiedzenia 1.
"""

import os
import requests
from utils import (
    load_json, save_json, load_meta, save_meta, now_iso
)

API_BASE = "https://api.sejm.gov.pl/sejm"
KADENCJA = "term10"
FOLDER = "glosowania"


def pobierz_posiedzenia():
    url = f"{API_BASE}/{KADENCJA}/proceedings"
    resp = requests.get(url, timeout=40)
    resp.raise_for_status()
    return resp.json()


def pobierz_szczegoly_glosowania(posiedzenie_nr, numer_glosowania):
    """Pobiera pełne szczegóły jednego głosowania (z listą votes każdego posła)"""
    url = f"{API_BASE}/{KADENCJA}/votings/{posiedzenie_nr}/{numer_glosowania}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    print("\n=== Aktualizacja głosowań Z PEŁNYMI GŁOSAMI POSŁÓW ===")

    meta = load_meta()
    ostatnie_posiedzenie = meta.get("glosowania", {}).get("ostatnie_posiedzenie", 0)
    print(f"  Ostatnie zapisane posiedzenie: {ostatnie_posiedzenie}")

    glosowania_dir = os.path.join(os.path.dirname(__file__), "..", "data", FOLDER)
    os.makedirs(glosowania_dir, exist_ok=True)

    posiedzenia = pobierz_posiedzenia()
    # Pobieramy wszystkie posiedzenia od 1 wzwyż
    do_pobrania = [p for p in posiedzenia if p.get("number", 0) >= 1]

    print(f"  Znaleziono {len(do_pobrania)} posiedzeń do aktualizacji pełnymi głosami.\n")

    najnowsze_nr = 0

    for pos in sorted(do_pobrania, key=lambda p: p["number"]):
        nr = pos["number"]
        print(f"  Aktualizuję posiedzenie nr {nr}...")

        try:
            lista_glosowan = requests.get(f"{API_BASE}/{KADENCJA}/votings/{nr}", timeout=30).json()

            pełne_glosowania = []
            for g in lista_glosowan:
                try:
                    szczegoly = pobierz_szczegoly_glosowania(nr, g["votingNumber"])
                    pełne_glosowania.append(szczegoly)
                except Exception as e:
                    print(f"    Błąd przy głosowaniu nr {g.get('votingNumber')}: {e}")

            nazwa_pliku = f"{FOLDER}/posiedzenie_{nr}.json"
            save_json(nazwa_pliku, {
                "posiedzenie": nr,
                "data": pos.get("date", ""),
                "tytul": pos.get("title", ""),
                "glosowania": pełne_glosowania,
                "_pobrano": now_iso(),
                "_full_votes": True
            })

            print(f"  Zapisano posiedzenie {nr} — {len(pełne_glosowania)} głosowań z indywidualnymi głosami posłów\n")

            if nr > najnowsze_nr:
                najnowsze_nr = nr

        except Exception as e:
            print(f"  BŁĄD przy posiedzeniu {nr}: {e}")
            continue

    # Aktualizacja meta
    meta["glosowania"] = {
        "ostatnia_aktualizacja": now_iso(),
        "ostatnie_posiedzenie": najnowsze_nr,
    }
    save_meta(meta)

    print(f"\n=== Gotowe ===\nZaktualizowano do posiedzenia nr {najnowsze_nr}")


if __name__ == "__main__":
    main()