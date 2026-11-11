# Formula 1 Performance Analytics

**End-to-end Data Analyst portfolio project | Excel • SQL • Python • Power BI**

## Business scenario
As a Data Analyst at a motorsport analytics company. Management wants to understand historical Formula 1 performance, driver and constructor success, qualifying outcomes, season trends and pit-stop patterns.

## Project objectives
1. Identify the drivers and constructors with the most Grand Prix wins.
2. Explore how the F1 calendar has changed over time.
3. Measure the relationship between starting grid position and finishing position.
4. Calculate the historical pole-position-to-win conversion rate.
5. Explore pit-stop activity and race-level pit-stop patterns.
6. Prepare a clean analytical dataset and communicate findings in a BI dashboard.

## Dataset
The supplied archive contains 15 CSV tables:
`circuits`, `constructor_results`, `constructor_standings`, `constructors`, `driver_standings`, `drivers`, `lap_times`, `pit_stops`, `practice_sessions`, `qualifying`, `races`, `results`, `seasons`, `sprint_results`, and `status`.

The source tables cover seasons 1950–2026 in the supplied extract. Some of the latest-season data may be partial; always check race counts before making full-season comparisons.

## Repository structure
```text
f1-performance-analytics/
├── data/
│   ├── raw/                  # Original CSV files
│   └── processed/            # Clean analytical output
├── docs/
│   ├── data_dictionary.md
│   └── methodology.md
├── outputs/
│   ├── charts/
│   ├── tables/
│   └── project_summary.json
├── sql/
│   └── analysis.sql
├── src/
│   └── analysis.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Tools
- **Python (pandas, matplotlib):** data profiling, cleaning, joining and exploratory analysis.
- **SQL:** relational joins, aggregation, ranking, window functions and business questions.
- **Excel:** independent validation, PivotTables and exploratory summaries.
- **Power BI:** interactive executive dashboard (dashboard build guide can be added as a next step).

## Initial findings from the supplied extract
- Pole-position starts analysed: **1,179**
- Pole-position starts converted to wins: **510**
- Historical pole-to-win conversion: **43.26%**
- Correlation between grid number and finishing position: **0.411** (positive means a larger grid number tends to accompany a larger finishing-position number; correlation is not proof of causation).
- Most race wins in this extract: **Lewis Hamilton (106)**
- Constructor with most race wins in this extract: **Ferrari (251)**

## Analytical workflow
1. **Business understanding:** define questions and metrics.
2. **Data understanding:** inspect tables, row counts, types, nulls, duplicates and relationships.
3. **Data preparation:** standardise types, join dimensions, derive indicators and document assumptions.
4. **Exploratory analysis:** rank drivers/teams, study trends and qualifying outcomes.
5. **Validation:** reconcile row counts and independently verify key aggregations in SQL/Excel.
6. **Visualisation:** create charts and an executive Power BI dashboard.
7. **Communication:** explain what happened, why it matters, limitations and recommended next analysis.

## Metric definitions
- **Race win:** a result row where `positionOrder = 1`.
- **Podium:** a result row where `positionOrder` is 1, 2 or 3.
- **Pole start:** a result row where `grid = 1`.
- **Pole-to-win conversion:** pole starts with `positionOrder = 1` divided by all pole starts.
- **Grid/finish correlation:** Pearson correlation between numeric starting grid and numeric finishing order, excluding missing values. Smaller grid/finish values are better.

## Power BI pages
1. **Executive overview:** total races, drivers, constructors, wins, pole conversion.
2. **Driver performance:** top drivers, wins by season, podiums and points.
3. **Constructor performance:** team wins, points and season trends.
4. **Qualifying analysis:** grid position vs finishing position; pole conversion.
5. **Pit-stop analysis:** average/median duration, stop counts and race comparisons.

## Author
Muhd Muslim Abd Jamal | Data Analyst Portfolio
