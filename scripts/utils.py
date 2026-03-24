import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_json(filename):
    """Wczytuje plik JSON z folderu data/. Zwraca None jeśli plik nie istnieje."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    """Zapisuje dane do pliku JSON w folderze data/."""
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Zapisano: {filename}")


def load_meta():
    """Wczytuje meta.json lub zwraca pusty słownik."""
    meta = load_json("meta.json")
    return meta if meta else {}


def save_meta(meta):
    """Zapisuje meta.json."""
    save_json("meta.json", meta)


def now_iso():
    """Zwraca aktualny czas UTC w formacie ISO."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_iso():
    """Zwraca dzisiejszą datę w formacie YYYY-MM-DD."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def append_changelog(wpisy):
    """
    Dopisuje listę wpisów do data/changelog.json.
    Każdy wpis to słownik z kluczami: data, typ, oraz dodatkowe pola.
    """
    if not wpisy:
        return

    changelog = load_json("changelog.json")
    if changelog is None:
        changelog = []

    for wpis in wpisy:
        if "data" not in wpis:
            wpis["data"] = today_iso()
        changelog.append(wpis)

    # Sortuj od najnowszych
    changelog.sort(key=lambda x: x.get("data", ""), reverse=True)
    save_json("changelog.json", changelog)
    print(f"  Dodano {len(wpisy)} wpis(ów) do changelogu.")
