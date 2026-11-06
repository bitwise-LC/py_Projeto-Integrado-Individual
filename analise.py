"""Limpeza e estatística para o indicador individual."""

import io
import unicodedata

import numpy as np
import pandas as pd


REQUIRED = {"ano", "uf", "taxa_alfabetizacao"}
NUMERIC = ("taxa_alfabetizacao", "tempo_deslocamento_minutos")
ALIASES = {
    "taxa_de_alfabetizacao": "taxa_alfabetizacao",
    "taxa_de_alfabetizacao_pct": "taxa_alfabetizacao",
    "tempo_medio_deslocamento_minutos": "tempo_deslocamento_minutos",
    "tempo_de_deslocamento_minutos": "tempo_deslocamento_minutos",
    "cor_ou_raca": "cor_raca",
    "grupo_de_idade": "faixa_etaria",
    "nivel_de_instrucao": "nivel_instrucao",
    "unidade_da_federacao": "uf",
    "unidade_da_federacao_codigo": "uf",
}


def _slug(value):
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(c for c in value if not unicodedata.combining(c))
    return "_".join(value.strip().lower().replace("%", "pct").split()).replace("-", "_")


def carregar_arquivo(upload):
    raw = upload.getvalue()
    if upload.name.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(raw))
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(raw), sep=None, engine="python", encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Não foi possível ler o CSV. Salve-o em UTF-8 ou Latin-1.")


def limpar_dados(frame):
    df = frame.copy()
    df.columns = [ALIASES.get(_slug(col), _slug(col)) for col in df.columns]
    if df.columns.duplicated().any():
        raise ValueError("Há colunas duplicadas após a padronização dos nomes.")
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))

    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["uf"] = df["uf"].astype("string").str.strip().str.upper()
    for col in NUMERIC:
        if col in df:
            values = df[col].astype("string").str.strip().str.replace("%", "", regex=False)
            values = values.map(lambda x: x.replace(".", "").replace(",", ".") if pd.notna(x) and "," in x else x)
            df[col] = pd.to_numeric(values, errors="coerce")
    for col in ("municipio", "sexo", "cor_raca", "faixa_etaria", "nivel_instrucao"):
        if col in df:
            df[col] = df[col].astype("string").str.strip()

    df = df.dropna(subset=["ano", "uf", "taxa_alfabetizacao"])
    df = df[df["taxa_alfabetizacao"].between(0, 100)]
    if "tempo_deslocamento_minutos" in df:
        df.loc[~df["tempo_deslocamento_minutos"].between(0, 1440), "tempo_deslocamento_minutos"] = np.nan
    return df.drop_duplicates().reset_index(drop=True)


def estatisticas(series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None
    q1, mediana, q3 = values.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    modos = values.mode()
    return {
        "n": len(values), "media": values.mean(), "mediana": mediana,
        "moda": modos.iloc[0] if len(modos) == 1 else np.nan,
        "q1": q1, "q3": q3, "iqr": iqr,
        "amplitude": values.max() - values.min(),
        "variancia": values.var(ddof=1) if len(values) > 1 else 0.0,
        "desvio_padrao": values.std(ddof=1) if len(values) > 1 else 0.0,
        "outliers": int(((values < inferior) | (values > superior)).sum()),
        "limite_inferior": inferior, "limite_superior": superior,
    }
