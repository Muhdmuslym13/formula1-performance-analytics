from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
CHARTS = ROOT / "outputs" / "charts"
for folder in [PROCESSED, TABLES, CHARTS]:
    folder.mkdir(parents=True, exist_ok=True)

def load_tables():
    return {p.stem: pd.read_csv(p) for p in RAW.glob("*.csv")}

def profile_data(tables):
    rows = []
    for name, df in tables.items():
        rows.append({
            "table": name, "rows": len(df), "columns": len(df.columns),
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_cells": int(df.isna().sum().sum()),
            "missing_pct": round(df.isna().sum().sum() / df.size * 100, 2) if df.size else 0
        })
    profile = pd.DataFrame(rows)
    profile.to_csv(TABLES / "data_quality_profile.csv", index=False)
    return profile

def build_fact(t):
    results = t["results"].copy()
    for col in ["positionOrder", "grid", "points", "milliseconds", "fastestLapSpeed", "fastestLap"]:
        results[col] = pd.to_numeric(results[col], errors="coerce")
    results["is_winner"] = (results["positionOrder"] == 1).astype(int)
    results["is_podium"] = results["positionOrder"].between(1, 3).astype(int)
    results["is_pole"] = (results["grid"] == 1).astype(int)

    races = t["races"][["raceId", "year", "round", "name", "date", "circuitId"]]
    drivers = t["drivers"][["driverId", "forename", "surname", "nationality"]]
    constructors = t["constructors"][["constructorId", "name", "nationality"]]
    circuits = t["circuits"][["circuitId", "location", "country"]]

    df = results.merge(races, on="raceId", how="left", validate="many_to_one")
    df = df.merge(drivers, on="driverId", how="left", suffixes=("", "_driver"), validate="many_to_one")
    df = df.merge(constructors, on="constructorId", how="left", suffixes=("_race", "_constructor"), validate="many_to_one")
    df = df.merge(circuits, on="circuitId", how="left", validate="many_to_one")
    df["driver_name"] = (df["forename"].fillna("") + " " + df["surname"].fillna("")).str.strip()
    df["constructor_name"] = df["name_constructor"]
    df["race_name"] = df["name_race"]
    df["race_date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

def save_analysis(t, df):
    driver_wins = (df[df.is_winner == 1].groupby("driver_name")
                   .agg(wins=("resultId", "count"))
                   .sort_values("wins", ascending=False).reset_index())
    team_wins = (df[df.is_winner == 1].groupby("constructor_name")
                 .agg(wins=("resultId", "count"))
                 .sort_values("wins", ascending=False).reset_index())
    season = (df.groupby("year").agg(races=("raceId", "nunique"),
              entries=("resultId", "count"), wins=("is_winner", "sum"))
              .reset_index())
    pole = df[df.grid == 1]
    pole_metrics = pd.DataFrame([{
        "pole_starts": len(pole), "pole_wins": int(pole.is_winner.sum()),
        "pole_to_win_rate_pct": round(pole.is_winner.mean() * 100, 2)
    }])
    grid_finish = df.dropna(subset=["grid", "positionOrder"])
    corr = grid_finish[["grid", "positionOrder"]].corr().iloc[0, 1]

    driver_wins.to_csv(TABLES / "driver_wins.csv", index=False)
    team_wins.to_csv(TABLES / "constructor_wins.csv", index=False)
    season.to_csv(TABLES / "season_trends.csv", index=False)
    pole_metrics.to_csv(TABLES / "pole_to_win_rate.csv", index=False)

    pit = t["pit_stops"].copy()
    pit["milliseconds"] = pd.to_numeric(pit["milliseconds"], errors="coerce")
    pit_summary = pit.groupby("raceId").agg(
        pit_stops=("stop", "count"),
        avg_pit_ms=("milliseconds", "mean"),
        median_pit_ms=("milliseconds", "median")
    ).reset_index()
    pit_summary = pit_summary.merge(t["races"][["raceId", "year", "name"]], on="raceId", how="left")
    pit_summary["avg_pit_seconds"] = pit_summary["avg_pit_ms"] / 1000
    pit_summary.to_csv(TABLES / "pit_stop_summary_by_race.csv", index=False)

    cols = ["resultId","raceId","driverId","constructorId","year","round","race_name",
            "race_date","driver_name","nationality","constructor_name","grid","positionOrder",
            "positionText","points","laps","milliseconds","fastestLap","fastestLapTime",
            "fastestLapSpeed","statusId","is_winner","is_podium","is_pole","country","location"]
    df[cols].to_csv(PROCESSED / "f1_race_results_clean.csv", index=False)

    # Charts
    plt.figure(figsize=(10, 6))
    driver_wins.head(10).sort_values("wins").plot(kind="barh", x="driver_name", y="wins", legend=False)
    plt.title("Top 10 Drivers by Grand Prix Wins"); plt.xlabel("Race wins"); plt.ylabel("Driver")
    plt.tight_layout(); plt.savefig(CHARTS / "top_10_drivers.png", dpi=160); plt.close()

    plt.figure(figsize=(10, 6))
    team_wins.head(10).sort_values("wins").plot(kind="barh", x="constructor_name", y="wins", legend=False)
    plt.title("Top 10 Constructors by Grand Prix Wins"); plt.xlabel("Race wins"); plt.ylabel("Constructor")
    plt.tight_layout(); plt.savefig(CHARTS / "top_10_constructors.png", dpi=160); plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(season.year, season.races, marker="o", markersize=3)
    plt.title("Formula 1 Races per Season"); plt.xlabel("Season"); plt.ylabel("Number of races")
    plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(CHARTS / "races_per_season.png", dpi=160); plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(["Pole → Win", "Pole → No Win"],
            [int(pole.is_winner.sum()), int(len(pole) - pole.is_winner.sum())])
    plt.title("Outcome of Pole Position Starts"); plt.ylabel("Number of race starts")
    plt.tight_layout(); plt.savefig(CHARTS / "pole_to_win.png", dpi=160); plt.close()

    summary = {
        "race_result_rows": len(df), "pole_starts": len(pole),
        "pole_wins": int(pole.is_winner.sum()),
        "pole_to_win_rate_pct": round(float(pole.is_winner.mean() * 100), 2),
        "grid_finish_correlation": round(float(corr), 3),
        "top_driver": driver_wins.iloc[0].to_dict() if len(driver_wins) else {},
        "top_constructor": team_wins.iloc[0].to_dict() if len(team_wins) else {}
    }
    (ROOT / "outputs" / "project_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print("Analysis complete. Review outputs/tables, outputs/charts and data/processed.")

if __name__ == "__main__":
    tables = load_tables()
    profile_data(tables)
    fact = build_fact(tables)
    save_analysis(tables, fact)
