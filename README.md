# Committee
*An universal tool for checking commits on GitHub*

## Instrukce k testování balíčku

1. `tox`

Spustí testy popsané v `tox.ini` s použitím nahraných kazet v `test_my/fixtures/cassette_library`. Funguje offline.

## Znovu-nahrání kazet

Znovu-nahrání kazet vyžaduje určitý setup repozitářů. Pro jeho vytvoření použijte skript `test_my/test_environment/setup.sh`. Je třeba nastavit proměnné prostředí `GH_TOKEN` a `GH_USER`. Token musí příslušet danému uživateli a mít scope repo.

Skript využívá program [`hub`](https://hub.github.com/), který si **nejprve zprovozněte**.

Skript vytvoří na GitHubu 3 repozitáře:

* committee-basic
* committee-rules
* committee-radioactive

Pokud by vám to vadilo, použijte testovací účet k tomuto určený.
Commit status nelze na GitHub smazat, tudíž jedinou možností, jak vyčistit případný nepořádek je repozitáře smazat pomocí skriptu `test_my/test_environment/delete.sh` (potřeba scope `delete_repo`).

Dále smažte všechny kazety v `test_my/fixtures/cassette_library`.

Spuštěním 
```
python -m pytest -v test_my/
```
se smazané kazety znovu nahrají a zároveň se spustí testy.





