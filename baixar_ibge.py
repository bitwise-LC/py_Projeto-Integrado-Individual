"""Baixa a taxa de alfabetização por UF diretamente da API oficial do IBGE."""

from pathlib import Path
import csv
import gzip
import json
from urllib.parse import urlencode
from urllib.request import urlopen


URL = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/9543/periodos/2022/"
    "variaveis/2513?localidades=N3%5Ball%5D"
)
URL_DESLOCAMENTO = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/10333/periodos/2022/"
    "variaveis/13377?" + urlencode({
        "localidades": "N3[all]",
        "classificacao": "537[all]|1568[all]|58[95253]|86[95251]",
    })
)
UF_CODIGOS = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
    "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}


def consultar(url):
    with urlopen(url, timeout=45) as response:
        raw = response.read()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def salvar_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Base oficial salva em {path}")


def main():
    payload = consultar(URL)
    if not isinstance(payload, list) or not payload:
        raise ValueError("A API do IBGE não retornou a tabela esperada.")
    rows = []
    for result in payload[0].get("resultados", []):
        for item in result.get("series", []):
            local = item.get("localidade", {})
            uf = UF_CODIGOS.get(str(local.get("id")))
            value = item.get("serie", {}).get("2022")
            if uf and value not in (None, "-", "..."):
                rows.append({
                    "ano": 2022, "uf": uf,
                    "taxa_alfabetizacao": float(str(value).replace(",", ".")),
                    "fonte_alfabetizacao": "IBGE/Censo 2022, SIDRA 9543, variável 2513",
                })
    rows = list({row["uf"]: row for row in rows}.values())
    if len(rows) != 27:
        raise ValueError(f"Esperadas 27 UFs; recebidas {len(rows)}. Confira a resposta da API.")
    path = Path(__file__).parent / "dados" / "alfabetizacao_ibge_2022.csv"
    salvar_csv(path, sorted(rows, key=lambda row: row["uf"]))

    payload = consultar(URL_DESLOCAMENTO)
    commute_rows = []
    for result in payload[0].get("resultados", []):
        classes = {item["id"]: item["categoria"] for item in result["classificacoes"]}
        tempo_id, tempo_nome = next(iter(classes["537"].items()))
        nivel_id, nivel_nome = next(iter(classes["1568"].items()))
        for item in result.get("series", []):
            uf = UF_CODIGOS.get(str(item["localidade"]["id"]))
            value = item.get("serie", {}).get("2022")
            if uf and value not in (None, "-", "..."):
                commute_rows.append({
                    "ano": 2022, "uf": uf, "nivel_instrucao": nivel_nome,
                    "nivel_id": nivel_id, "faixa_tempo": tempo_nome,
                    "faixa_tempo_id": tempo_id, "pessoas": int(value),
                    "fonte": "IBGE/Censo 2022, SIDRA 10333, variável 13377",
                })
    if len(commute_rows) < 27 * 30:
        raise ValueError("A tabela de deslocamento veio incompleta; nenhum arquivo foi salvo.")
    path = Path(__file__).parent / "dados" / "deslocamento_ibge_2022.csv"
    salvar_csv(path, commute_rows)


if __name__ == "__main__":
    main()
