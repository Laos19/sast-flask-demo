"""Convierte un SARIF de CodeQL en un resumen de texto legible (para las evidencias).

Uso: python scripts/sarif_resumen.py <entrada.sarif> <salida.txt>
"""
import json
import sys


def nivel(score):
    # Escala que usa GitHub Code Scanning para "security-severity"
    if score is None:
        return "-"
    score = float(score)
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"


def main(entrada, salida):
    with open(entrada, encoding="utf-8") as f:
        run = json.load(f)["runs"][0]
    driver = run["tool"]["driver"]
    reglas = {}
    for comp in [driver] + run["tool"].get("extensions", []):
        for r in comp.get("rules", []):
            reglas[r["id"]] = r
    lineas = [
        f"Herramienta: {driver['name']} {driver.get('semanticVersion', '')}",
        f"Reglas ejecutadas: {len(reglas)}",
        f"Hallazgos: {len(run['results'])}",
        "",
    ]
    for res in sorted(run["results"], key=lambda r: r["locations"][0]["physicalLocation"]["region"]["startLine"]):
        regla = reglas.get(res["ruleId"], {})
        props = regla.get("properties", {})
        loc = res["locations"][0]["physicalLocation"]
        score = props.get("security-severity")
        cwes = [t.split("/")[-1].upper() for t in props.get("tags", []) if "cwe-" in t]
        lineas += [
            f">> [{res['ruleId']}] {regla.get('shortDescription', {}).get('text', '')}",
            f"   Nivel SARIF: {res.get('level', regla.get('defaultConfiguration', {}).get('level', ''))}"
            f" | security-severity: {score} ({nivel(score)}) | precisión: {props.get('precision', '-')}",
            f"   CWE: {', '.join(cwes) or '-'}",
            f"   Ubicación: {loc['artifactLocation']['uri']}:{loc['region']['startLine']}",
            f"   Mensaje: {res['message']['text']}",
        ]
        for flujo in res.get("codeFlows", [])[:1]:
            pasos = flujo["threadFlows"][0]["locations"]
            lineas.append("   Flujo de datos (fuente -> sumidero):")
            for p in pasos:
                pl = p["location"]["physicalLocation"]
                lineas.append(f"     línea {pl['region']['startLine']}: {p['location'].get('message', {}).get('text', '')}")
        lineas.append("-" * 60)
    with open(salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print("\n".join(lineas))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
