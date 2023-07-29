-- Constrain Time Range to [2020-01-01T00:00:00, 2020-01-02T00:00:00]
SELECT
  subq_2.ds
  , subq_2.metric_time
  , subq_2.bookings
FROM (
  -- Metric Time Dimension 'ds'
  SELECT
    subq_1.ds
    , subq_1.ds AS metric_time
    , subq_1.bookings
  FROM (
    -- Pass Only Elements:
    --   ['bookings', 'ds']
    SELECT
      subq_0.ds
      , subq_0.bookings
    FROM (
      -- Read Elements From Semantic Model 'bookings_source'
      SELECT
        1 AS bookings
        , CASE WHEN is_instant THEN 1 ELSE 0 END AS instant_bookings
        , bookings_source_src_10001.booking_value
        , bookings_source_src_10001.booking_value AS max_booking_value
        , bookings_source_src_10001.booking_value AS min_booking_value
        , bookings_source_src_10001.guest_id AS bookers
        , bookings_source_src_10001.booking_value AS average_booking_value
        , bookings_source_src_10001.booking_value AS booking_payments
        , CASE WHEN referrer_id IS NOT NULL THEN 1 ELSE 0 END AS referred_bookings
        , bookings_source_src_10001.booking_value AS median_booking_value
        , bookings_source_src_10001.booking_value AS booking_value_p99
        , bookings_source_src_10001.booking_value AS discrete_booking_value_p99
        , bookings_source_src_10001.booking_value AS approximate_continuous_booking_value_p99
        , bookings_source_src_10001.booking_value AS approximate_discrete_booking_value_p99
        , bookings_source_src_10001.is_instant
        , bookings_source_src_10001.ds
        , DATE_TRUNC(bookings_source_src_10001.ds, isoweek) AS ds__week
        , DATE_TRUNC(bookings_source_src_10001.ds, month) AS ds__month
        , DATE_TRUNC(bookings_source_src_10001.ds, quarter) AS ds__quarter
        , DATE_TRUNC(bookings_source_src_10001.ds, isoyear) AS ds__year
        , bookings_source_src_10001.ds_partitioned
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, isoweek) AS ds_partitioned__week
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, month) AS ds_partitioned__month
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, quarter) AS ds_partitioned__quarter
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, isoyear) AS ds_partitioned__year
        , bookings_source_src_10001.paid_at
        , DATE_TRUNC(bookings_source_src_10001.paid_at, isoweek) AS paid_at__week
        , DATE_TRUNC(bookings_source_src_10001.paid_at, month) AS paid_at__month
        , DATE_TRUNC(bookings_source_src_10001.paid_at, quarter) AS paid_at__quarter
        , DATE_TRUNC(bookings_source_src_10001.paid_at, isoyear) AS paid_at__year
        , bookings_source_src_10001.is_instant AS booking__is_instant
        , bookings_source_src_10001.ds AS booking__ds
        , DATE_TRUNC(bookings_source_src_10001.ds, isoweek) AS booking__ds__week
        , DATE_TRUNC(bookings_source_src_10001.ds, month) AS booking__ds__month
        , DATE_TRUNC(bookings_source_src_10001.ds, quarter) AS booking__ds__quarter
        , DATE_TRUNC(bookings_source_src_10001.ds, isoyear) AS booking__ds__year
        , bookings_source_src_10001.ds_partitioned AS booking__ds_partitioned
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, isoweek) AS booking__ds_partitioned__week
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, month) AS booking__ds_partitioned__month
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, quarter) AS booking__ds_partitioned__quarter
        , DATE_TRUNC(bookings_source_src_10001.ds_partitioned, isoyear) AS booking__ds_partitioned__year
        , bookings_source_src_10001.paid_at AS booking__paid_at
        , DATE_TRUNC(bookings_source_src_10001.paid_at, isoweek) AS booking__paid_at__week
        , DATE_TRUNC(bookings_source_src_10001.paid_at, month) AS booking__paid_at__month
        , DATE_TRUNC(bookings_source_src_10001.paid_at, quarter) AS booking__paid_at__quarter
        , DATE_TRUNC(bookings_source_src_10001.paid_at, isoyear) AS booking__paid_at__year
        , bookings_source_src_10001.listing_id AS listing
        , bookings_source_src_10001.guest_id AS guest
        , bookings_source_src_10001.host_id AS host
        , bookings_source_src_10001.listing_id AS booking__listing
        , bookings_source_src_10001.guest_id AS booking__guest
        , bookings_source_src_10001.host_id AS booking__host
      FROM ***************************.fct_bookings bookings_source_src_10001
    ) subq_0
  ) subq_1
) subq_2
WHERE subq_2.metric_time BETWEEN CAST('2020-01-01' AS DATETIME) AND CAST('2020-01-02' AS DATETIME)
