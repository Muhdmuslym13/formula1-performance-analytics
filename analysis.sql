-- Formula 1 Performance Analytics
-- Assumption: CSV tables have been imported into SQLite with their source names.
-- Use SQLite-compatible SQL. Quote "position" only if your SQL dialect requires it.

-- 1. Top 10 drivers by race wins
SELECT d.driverId,
       d.forename || ' ' || d.surname AS driver_name,
       COUNT(*) AS race_wins
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE r.positionOrder = 1
GROUP BY d.driverId, driver_name
ORDER BY race_wins DESC
LIMIT 10;

-- 2. Top 10 constructors by race wins
SELECT c.constructorId, c.name AS constructor_name,
       COUNT(*) AS race_wins
FROM results r
JOIN constructors c ON r.constructorId = c.constructorId
WHERE r.positionOrder = 1
GROUP BY c.constructorId, c.name
ORDER BY race_wins DESC
LIMIT 10;

-- 3. Number of races per season
SELECT ra.year, COUNT(DISTINCT ra.raceId) AS races_held
FROM races ra
GROUP BY ra.year
ORDER BY ra.year;

-- 4. Pole-position conversion rate
SELECT COUNT(*) AS pole_starts,
       SUM(CASE WHEN positionOrder = 1 THEN 1 ELSE 0 END) AS pole_wins,
       ROUND(100.0 * SUM(CASE WHEN positionOrder = 1 THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 2) AS pole_to_win_pct
FROM results
WHERE grid = 1;

-- 5. Starting grid vs finishing position (inspect records)
SELECT ra.year, ra.name AS race_name,
       d.forename || ' ' || d.surname AS driver_name,
       r.grid, r.positionOrder AS finish_position
FROM results r
JOIN races ra ON r.raceId = ra.raceId
JOIN drivers d ON r.driverId = d.driverId
WHERE r.grid > 0 AND r.positionOrder IS NOT NULL
ORDER BY ra.year, ra.round, r.grid;

-- 6. Driver podiums by season
SELECT ra.year, d.forename || ' ' || d.surname AS driver_name,
       COUNT(*) AS podiums
FROM results r
JOIN races ra ON r.raceId = ra.raceId
JOIN drivers d ON r.driverId = d.driverId
WHERE r.positionOrder BETWEEN 1 AND 3
GROUP BY ra.year, d.driverId, driver_name
ORDER BY ra.year, podiums DESC;

-- 7. Constructor points by season
SELECT ra.year, c.name AS constructor_name,
       SUM(r.points) AS points
FROM results r
JOIN races ra ON r.raceId = ra.raceId
JOIN constructors c ON r.constructorId = c.constructorId
GROUP BY ra.year, c.constructorId, c.name
ORDER BY ra.year, points DESC;

-- 8. Pit-stop summary by race
SELECT ra.year, ra.name AS race_name,
       COUNT(*) AS pit_stop_count,
       ROUND(AVG(p.milliseconds) / 1000.0, 2) AS avg_pit_seconds,
       ROUND(MIN(p.milliseconds) / 1000.0, 2) AS fastest_pit_seconds
FROM pit_stops p
JOIN races ra ON p.raceId = ra.raceId
WHERE p.milliseconds IS NOT NULL
GROUP BY ra.raceId, ra.year, ra.name
ORDER BY ra.year, ra.round;

-- 9. Rank drivers by wins using a window function
WITH driver_wins AS (
    SELECT d.driverId, d.forename || ' ' || d.surname AS driver_name,
           COUNT(*) AS wins
    FROM results r
    JOIN drivers d ON r.driverId = d.driverId
    WHERE r.positionOrder = 1
    GROUP BY d.driverId, driver_name
)
SELECT driver_name, wins,
       DENSE_RANK() OVER (ORDER BY wins DESC) AS win_rank
FROM driver_wins
ORDER BY win_rank, driver_name;

-- 10. Compare qualifying position with race finish
SELECT q.raceId,
       d.forename || ' ' || d.surname AS driver_name,
       CAST(q.position AS INTEGER) AS qualifying_position,
       r.positionOrder AS race_finish
FROM qualifying q
JOIN results r ON q.raceId = r.raceId AND q.driverId = r.driverId
JOIN drivers d ON q.driverId = d.driverId
WHERE q.position IS NOT NULL AND r.positionOrder IS NOT NULL;
