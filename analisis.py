# pip install pandas requests beautifulsoup4 lxml geopandas shapely

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass
class City:
    name: str
    dept_code: int
    mun_code: int


BARRANQUILLA = City("BARRANQUILLA", dept_code=3, mun_code=1)


def norm(s: str) -> str:
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s


def to_int(s: str) -> int:
    return int(str(s).replace(",", "").replace(".", "").strip())


def fetch_colombia_com_result(year: int, city: City) -> tuple[pd.DataFrame, dict]:
    """
    Fetches municipal first-round presidential results from Colombia.com pages.

    Colombia.com labels these pages as data supplied by Registraduría.
    Example:
    https://www.colombia.com/elecciones/2026/resultados/primera-vuelta.aspx?C=P1&D=3&M=1
    """
    url = (
        f"https://www.colombia.com/elecciones/{year}/resultados/primera-vuelta.aspx"
        f"?C=P1&D={city.dept_code}&M={city.mun_code}"
    )

    html = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 election-analysis-script"},
    ).text

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    meta = {"year": year, "city": city.name, "url": url}

    def grab(label: str, percent: bool = False):
        if percent:
            pat = rf"{label}:\s*([\d,\.]+)\s+([\d,\.]+)\s*%"
        else:
            pat = rf"{label}:\s*([\d,\.]+)"
        m = re.search(pat, text, flags=re.I)
        if not m:
            return None
        return m.groups() if percent else m.group(1)

    meta["mesas_instaladas"] = grab("Mesas instaladas")
    meta["mesas_informadas"] = grab("Mesas informadas", percent=True)
    meta["potencial_sufragantes"] = grab("Potencial sufragantes")
    meta["total_sufragantes"] = grab("Total sufragantes", percent=True)

    # Candidate parser for the Colombia.com text layout.
    rows = []
    in_candidates = False

    for i, line in enumerate(lines):
        if "Candidato" in line and "Votos" in line:
            in_candidates = True
            continue
        if in_candidates and "Total votos por candidato" in line:
            break
        if not in_candidates:
            continue

        m = re.match(r"^(\d{2})\s+(.+)$", line)
        if not m:
            continue

        code = m.group(1)
        candidate = re.sub(r"^Image:\s*", "", m.group(2)).strip()

        if i + 1 >= len(lines):
            continue

        party_line = lines[i + 1]
        m2 = re.match(r"^(.+?)\s+([\d,]+)\s+([\d\.]+)\s*%$", party_line)
        if not m2:
            continue

        party, votes, pct = m2.groups()
        rows.append(
            {
                "year": year,
                "city": city.name,
                "candidate_code": code,
                "candidate": candidate,
                "candidate_norm": norm(candidate),
                "party": party.strip(),
                "votes": to_int(votes),
                "pct": float(pct),
            }
        )

    df = pd.DataFrame(rows).sort_values("votes", ascending=False).reset_index(drop=True)
    return df, meta


def candidate_votes(df: pd.DataFrame, contains: str) -> tuple[int, float]:
    key = norm(contains)
    hit = df[df["candidate_norm"].str.contains(key, regex=False)]
    if hit.empty:
        raise ValueError(f"No candidate matched: {contains}")
    return int(hit.iloc[0]["votes"]), float(hit.iloc[0]["pct"])


def block_votes(df: pd.DataFrame, names: Iterable[str]) -> tuple[int, float]:
    votes = 0
    pct = 0.0
    for name in names:
        v, p = candidate_votes(df, name)
        votes += v
        pct += p
    return votes, pct


def barranquilla_topline():
    city = BARRANQUILLA
    r2022, m2022 = fetch_colombia_com_result(2022, city)
    r2026, m2026 = fetch_colombia_com_result(2026, city)

    petro_v, petro_p = candidate_votes(r2022, "GUSTAVO PETRO")
    cepeda_v, cepeda_p = candidate_votes(r2026, "IVAN CEPEDA")
    abelardo_v, abelardo_p = candidate_votes(r2026, "ABELARDO")
    fajardo22_v, fajardo22_p = candidate_votes(r2022, "SERGIO FAJARDO")
    fajardo26_v, fajardo26_p = candidate_votes(r2026, "SERGIO FAJARDO")

    right22_v, right22_p = block_votes(
        r2022, ["FEDERICO GUTIERREZ", "RODOLFO HERNANDEZ"]
    )

    print("\nTOP 2026")
    print(r2026[["candidate", "votes", "pct"]].head(8).to_string(index=False))

    print("\nCOMPARACIÓN BARRANQUILLA")
    print(f"Petro 2022:  {petro_v:,} votos | {petro_p:.2f}%")
    print(f"Cepeda 2026: {cepeda_v:,} votos | {cepeda_p:.2f}%")
    print(f"Cambio izquierda: {cepeda_v - petro_v:+,} votos | {cepeda_p - petro_p:+.2f} pp")

    print(f"\nFico+Rodolfo 2022: {right22_v:,} votos | {right22_p:.2f}%")
    print(f"Abelardo 2026:     {abelardo_v:,} votos | {abelardo_p:.2f}%")
    print(f"Cambio bloque derecha/anti-Pacto: {abelardo_v - right22_v:+,} votos | {abelardo_p - right22_p:+.2f} pp")

    print(f"\nMargen Cepeda-Abelardo 2026: {cepeda_v - abelardo_v:,} votos | {cepeda_p - abelardo_p:.2f} pp")
    print(f"Fajardo: {fajardo22_v:,} ({fajardo22_p:.2f}%) → {fajardo26_v:,} ({fajardo26_p:.2f}%)")


# ---------- Optional barrio / polling-place layer ----------

def load_barranquilla_barrios():
    """
    Official Barranquilla ArcGIS barrios layer.
    Fields include: NOMBRE, LOCALIDAD, CS.
    """
    import geopandas as gpd

    barrios_url = (
        "https://services2.arcgis.com/Fcuj0xkCSDfdj9EJ/ArcGIS/rest/services/"
        "panorama/MapServer/3/query?"
        "where=1%3D1&outFields=*&returnGeometry=true&f=geojson"
    )
    barrios = gpd.read_file(barrios_url).to_crs(4326)
    return barrios


def aggregate_polling_places_to_barrios(
    polling_places_csv: str,
    results_by_place_csv: str,
    place_id_col: str = "puesto_id",
    lat_col: str = "lat",
    lon_col: str = "lon",
):
    """
    Expected polling_places_csv columns:
        puesto_id, puesto_nombre, lat, lon

    Expected results_by_place_csv columns:
        puesto_id, candidate, votes

    This assigns each polling place to a Barranquilla barrio polygon, then aggregates.
    """
    import geopandas as gpd
    from shapely.geometry import Point

    barrios = load_barranquilla_barrios()

    puestos = pd.read_csv(polling_places_csv)
    geometry = [Point(xy) for xy in zip(puestos[lon_col], puestos[lat_col])]
    puestos_gdf = gpd.GeoDataFrame(puestos, geometry=geometry, crs="EPSG:4326")

    joined = gpd.sjoin(
        puestos_gdf,
        barrios[["NOMBRE", "LOCALIDAD", "geometry"]],
        how="left",
        predicate="within",
    )

    votes = pd.read_csv(results_by_place_csv)
    votes["candidate_norm"] = votes["candidate"].map(norm)

    merged = votes.merge(
        joined[[place_id_col, "NOMBRE", "LOCALIDAD"]],
        on=place_id_col,
        how="left",
    )

    by_barrio = (
        merged.groupby(["NOMBRE", "LOCALIDAD", "candidate_norm"], dropna=False)["votes"]
        .sum()
        .reset_index()
    )

    total = by_barrio.groupby(["NOMBRE", "LOCALIDAD"])["votes"].transform("sum")
    by_barrio["pct"] = 100 * by_barrio["votes"] / total

    winner = (
        by_barrio.sort_values(["NOMBRE", "votes"], ascending=[True, False])
        .groupby(["NOMBRE", "LOCALIDAD"])
        .head(1)
        .rename(columns={"candidate_norm": "winner", "pct": "winner_pct"})
    )

    return by_barrio, winner


if __name__ == "__main__":
    barranquilla_topline()
