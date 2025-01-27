-- Compute Metrics via Expressions
SELECT
  metric_time
  , delayed_bookings * 2 AS double_counted_delayed_bookings
FROM (
  -- Constrain Output with WHERE
  -- Pass Only Elements:
  --   ['bookings', 'metric_time']
  -- Aggregate Measures
  SELECT
    metric_time
    , SUM(bookings) AS delayed_bookings
  FROM (
    -- Read Elements From Data Source 'bookings_source'
    -- Metric Time Dimension 'ds'
    -- Pass Only Elements:
    --   ['bookings', 'is_instant', 'metric_time']
    SELECT
      ds AS metric_time
      , is_instant
      , 1 AS bookings
    FROM (
      -- User Defined SQL Query
      SELECT * FROM ***************************.fct_bookings
    ) bookings_source_src_10001
  ) subq_8
  WHERE NOT is_instant
  GROUP BY
    metric_time
) subq_11
