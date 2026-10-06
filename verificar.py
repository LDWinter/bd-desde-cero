"""Verificador de etapas. Uso:  python3 verificar.py <número de etapa>

Revisa tu trabajo de cada etapa y te dice qué está bien (✔) y qué falta (✘).
Se va ampliando con cada lección nueva.
"""
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
ok = True


def chequear(condicion, mensaje_bien, mensaje_mal):
    global ok
    if condicion:
        print("  ✔", mensaje_bien)
    else:
        print("  ✘", mensaje_mal)
        ok = False


def etapa_0():
    db = AQUI / "etapa-00" / "practica.db"
    chequear(db.exists(), "existe etapa-00/practica.db", "no encuentro etapa-00/practica.db (creala con DB Browser)")
    if db.exists():
        chequear(db.read_bytes()[:16] == b"SQLite format 3\x00", "es una base SQLite válida",
                 "el archivo existe pero no es una base SQLite")


ETAPAS = {0: etapa_0}

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Uso: python3 verificar.py <número de etapa>   (ej.: python3 verificar.py 0)")
    n = int(sys.argv[1])
    if n not in ETAPAS:
        sys.exit(f"La etapa {n} todavía no tiene verificador: se agrega cuando veamos esa lección.")
    print(f"Etapa {n}:")
    ETAPAS[n]()
    print("\n🎉 ¡Etapa superada!" if ok else "\nTodavía falta algo: revisá los ✘ de arriba.")
    sys.exit(0 if ok else 1)
