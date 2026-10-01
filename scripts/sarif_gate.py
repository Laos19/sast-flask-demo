"""Quality gate para SARIF: falla (exit 1) si hay hallazgos con security-severity >= umbral.

CodeQL nunca rompe el pipeline por sí solo; este script lo hace a partir de su SARIF.
Uso: python scripts/sarif_gate.py <archivo.sarif> [umbral=7.0]   (7.0 = High o Critical)
"""
import json
import sys


def main(ruta, umbral):
    with open(ruta, encoding="utf-8") as f:
        sarif = json.load(f)
    bloqueantes = []
    for run in sarif["runs"]:
        # Las reglas pueden venir en el driver o en las extensiones (paquetes de consultas)
        severidad = {}
        for comp in [run["tool"]["driver"]] + run["tool"].get("extensions", []):
            for regla in comp.get("rules", []):
                severidad[regla["id"]] = float(regla.get("properties", {}).get("security-severity", 0))
        for res in run["results"]:
            score = severidad.get(res["ruleId"], 0)
            if score >= umbral:
                loc = res["locations"][0]["physicalLocation"]
                bloqueantes.append(f"{res['ruleId']} ({score}) en {loc['artifactLocation']['uri']}:{loc['region']['startLine']}")
    for b in bloqueantes:
        print(f"::error::{b}")
    print(f"Hallazgos con security-severity >= {umbral}: {len(bloqueantes)}")
    sys.exit(1 if bloqueantes else 0)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 7.0)
