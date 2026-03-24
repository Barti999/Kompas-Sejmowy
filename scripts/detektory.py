# ============================================================
# DETEKTORY ZMIAN POSŁÓW
# Każdy detektor opisuje jedno pole które skrypt ma śledzić.
#
# Żeby dodać nowy typ zmiany — skopiuj jeden blok poniżej,
# zmień "pole", "typ_zmiany" i "opis". Reszta działa sama.
# ============================================================

DETEKTORY_POSLOW = [
    {
        "pole":        "club",
        "typ_zmiany":  "zmiana_klubu",
        "opis":        "Poseł zmienił klub lub koło poselskie",
        "zapisz_hist": True,   # dopisuje wpis do clubHistory w rekordzie posła
    },
    {
        "pole":        "active",
        "typ_zmiany":  "zmiana_aktywnosci",
        "opis":        "Poseł utracił lub odzyskał mandat",
        "zapisz_hist": True,
    },
    {
        "pole":        "email",
        "typ_zmiany":  "zmiana_emaila",
        "opis":        "Zmiana adresu email posła",
        "zapisz_hist": False,
    },
    {
        "pole":        "districtNum",
        "typ_zmiany":  "zmiana_okregu",
        "opis":        "Poseł zmienił okręg wyborczy",
        "zapisz_hist": False,
    },
    # -------------------------------------------------------
    # DODAJ TUTAJ NOWE DETEKTORY
    # Przykład:
    # {
    #     "pole":        "profession",
    #     "typ_zmiany":  "zmiana_zawodu",
    #     "opis":        "Zmiana zawodu lub funkcji posła",
    #     "zapisz_hist": False,
    # },
    # -------------------------------------------------------
]


# ============================================================
# DETEKTORY ZMIAN KLUBÓW
# ============================================================

DETEKTORY_KLUBOW = [
    {
        "pole":       "name",
        "typ_zmiany": "zmiana_nazwy_klubu",
        "opis":       "Klub lub koło zmieniło nazwę",
    },
    {
        "pole":       "membersCount",
        "typ_zmiany": "zmiana_liczby_czlonkow",
        "opis":       "Zmiana liczby członków klubu lub koła",
    },
    # -------------------------------------------------------
    # DODAJ TUTAJ NOWE DETEKTORY KLUBÓW
    # -------------------------------------------------------
]
