"""
update_poslowie.py
------------------
Pobiera listę posłów z Sejm API i porównuje ze stanem lokalnym.
Wykrywa: nowych posłów, zmiany pól, wygaśnięcia mandatów.
Zapisuje zmiany do data/poslowie.json i data/changelog.json.
"""

import requests
from utils import (
    load_json, save_json, load_meta, save_meta,
    now_iso, today_iso, append_changelog
)
from detektory import DETEKTORY_POSLOW

API_BASE    = "https://api.sejm.gov.pl/sejm"
KADENCJA    = "term10"
PLIK_POSLOW = "poslowie.json"


def pobierz_poslow_z_api():
    """Pobiera pełną listę posłów z Sejm API."""
    url = f"{API_BASE}/{KADENCJA}/MP"
    print(f"  Pobieram: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def buduj_slownik(lista, klucz="id"):
    """Zamienia listę rekordów na słownik {klucz: rekord}."""
    return {str(r[klucz]): r for r in lista}


def inicjalizuj_rekord(posel_api):
    """Tworzy nowy pełny rekord posła z danymi z API + historia."""
    rekord = dict(posel_api)
    rekord["clubHistory"] = [
        {
            "club": posel_api.get("club", ""),
            "od":   today_iso(),
            "do":   None
        }
    ]
    rekord["activeHistory"] = [
        {
            "active": posel_api.get("active", True),
            "od":     today_iso(),
            "powod":  None
        }
    ]
    rekord["_zaktualizowano"] = now_iso()
    return rekord


def zaktualizuj_history(rekord, pole, nowa_wartosc):
    """Zamyka poprzedni wpis w historii i dodaje nowy."""
    if pole == "club":
        historia = rekord.setdefault("clubHistory", [])
    elif pole == "active":
        historia = rekord.setdefault("activeHistory", [])
    else:
        return

    # Zamknij ostatni otwarty wpis
    if historia and historia[-1].get("do") is None:
        historia[-1]["do"] = today_iso()

    # Dodaj nowy wpis
    nowy = {"od": today_iso(), "do": None}
    if pole == "club":
        nowy["club"] = nowa_wartosc
    elif pole == "active":
        nowy["active"] = nowa_wartosc
        nowy["powod"] = None
    historia.append(nowy)


def main():
    print("\n=== Aktualizacja posłów ===")

    # 1. Wczytaj stan lokalny
    lokalne = load_json(PLIK_POSLOW)
    if lokalne is None:
        print("  Brak lokalnego pliku — pierwsze uruchomienie.")
        lokalne = []
    slownik_lokalny = buduj_slownik(lokalne)

    # 2. Pobierz aktualny stan z API
    api_lista = pobierz_poslow_z_api()
    slownik_api = buduj_slownik(api_lista)
    print(f"  API zwróciło {len(api_lista)} posłów.")

    zmiany_changelog = []
    licznik = {"nowi": 0, "zmienieni": 0, "bez_zmian": 0}

    # 3. Przejdź przez każdego posła z API
    for posel_id, posel_api in slownik_api.items():

        # --- NOWY POSEŁ ---
        if posel_id not in slownik_lokalny:
            nowy_rekord = inicjalizuj_rekord(posel_api)
            slownik_lokalny[posel_id] = nowy_rekord
            licznik["nowi"] += 1
            zmiany_changelog.append({
                "typ":        "nowy_posel",
                "posel_id":   posel_id,
                "nazwisko":   posel_api.get("lastFirstName", ""),
                "klub":       posel_api.get("club", ""),
            })
            print(f"  [NOWY]     {posel_api.get('lastFirstName')} (id: {posel_id})")
            continue

        # --- ISTNIEJĄCY POSEŁ — sprawdź detektory ---
        rekord_lokalny = slownik_lokalny[posel_id]
        zmieniony = False

        for detektor in DETEKTORY_POSLOW:
            pole        = detektor["pole"]
            typ_zmiany  = detektor["typ_zmiany"]
            zapisz_hist = detektor.get("zapisz_hist", False)

            stara_wartosc = rekord_lokalny.get(pole)
            nowa_wartosc  = posel_api.get(pole)

            if stara_wartosc != nowa_wartosc:
                print(f"  [ZMIANA]   {posel_api.get('lastFirstName')} — {pole}: {stara_wartosc} → {nowa_wartosc}")

                # Zaktualizuj pole w rekordzie
                rekord_lokalny[pole] = nowa_wartosc

                # Dopisz do historii jeśli wymagane
                if zapisz_hist:
                    zaktualizuj_history(rekord_lokalny, pole, nowa_wartosc)

                # Dopisz do changelogu
                zmiany_changelog.append({
                    "typ":       typ_zmiany,
                    "opis":      detektor["opis"],
                    "posel_id":  posel_id,
                    "nazwisko":  posel_api.get("lastFirstName", ""),
                    "z":         str(stara_wartosc),
                    "na":        str(nowa_wartosc),
                })
                zmieniony = True

        if zmieniony:
            rekord_lokalny["_zaktualizowano"] = now_iso()
            licznik["zmienieni"] += 1
        else:
            licznik["bez_zmian"] += 1

    # 4. Zapisz tylko jeśli były zmiany
    if licznik["nowi"] > 0 or licznik["zmienieni"] > 0:
        wynik = list(slownik_lokalny.values())
        save_json(PLIK_POSLOW, wynik)
        append_changelog(zmiany_changelog)

        meta = load_meta()
        meta["poslowie"] = {
            "ostatnia_aktualizacja": now_iso(),
            "liczba_poslow":         len(wynik),
        }
        save_meta(meta)
    else:
        print("  Brak zmian — plik nie został nadpisany.")

    print(f"\n  Podsumowanie: {licznik['nowi']} nowych, "
          f"{licznik['zmienieni']} zmienionych, "
          f"{licznik['bez_zmian']} bez zmian.")
    print("=== Gotowe ===\n")


if __name__ == "__main__":
    main()
