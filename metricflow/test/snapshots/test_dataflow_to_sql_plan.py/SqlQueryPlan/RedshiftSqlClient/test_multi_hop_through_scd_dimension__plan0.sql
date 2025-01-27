-- Compute Metrics via Expressions
SELECT
  subq_10.metric_time
  , subq_10.listing__user__home_state_latest
  , subq_10.bookings
FROM (
  -- Aggregate Measures
  SELECT
    subq_9.metric_time
    , subq_9.listing__user__home_state_latest
    , SUM(subq_9.bookings) AS bookings
  FROM (
    -- Pass Only Elements:
    --   ['bookings', 'listing__user__home_state_latest', 'metric_time']
    SELECT
      subq_8.metric_time
      , subq_8.listing__user__home_state_latest
      , subq_8.bookings
    FROM (
      -- Join Standard Outputs
      SELECT
        subq_2.metric_time AS metric_time
        , subq_7.window_start AS listing__window_start
        , subq_7.window_end AS listing__window_end
        , subq_2.listing AS listing
        , subq_7.user__home_state_latest AS listing__user__home_state_latest
        , subq_2.bookings AS bookings
      FROM (
        -- Pass Only Elements:
        --   ['bookings', 'metric_time', 'listing']
        SELECT
          subq_1.metric_time
          , subq_1.listing
          , subq_1.bookings
        FROM (
          -- Metric Time Dimension 'ds'
          SELECT
            subq_0.ds
            , subq_0.ds__week
            , subq_0.ds__month
            , subq_0.ds__quarter
            , subq_0.ds__year
            , subq_0.ds_partitioned
            , subq_0.ds_partitioned__week
            , subq_0.ds_partitioned__month
            , subq_0.ds_partitioned__quarter
            , subq_0.ds_partitioned__year
            , subq_0.booking_paid_at
            , subq_0.booking_paid_at__week
            , subq_0.booking_paid_at__month
            , subq_0.booking_paid_at__quarter
            , subq_0.booking_paid_at__year
            , subq_0.ds AS metric_time
            , subq_0.ds__week AS metric_time__week
            , subq_0.ds__month AS metric_time__month
            , subq_0.ds__quarter AS metric_time__quarter
            , subq_0.ds__year AS metric_time__year
            , subq_0.listing
            , subq_0.guest
            , subq_0.host
            , subq_0.user
            , subq_0.is_instant
            , subq_0.bookings
            , subq_0.instant_bookings
            , subq_0.booking_value
            , subq_0.bookers
            , subq_0.average_booking_value
          FROM (
            -- Read Elements From Data Source 'bookings_source'
            SELECT
              1 AS bookings
              , CASE WHEN is_instant THEN 1 ELSE 0 END AS instant_bookings
              , bookings_source_src_10018.booking_value
              , bookings_source_src_10018.guest_id AS bookers
              , bookings_source_src_10018.booking_value AS average_booking_value
              , bookings_source_src_10018.booking_value AS booking_payments
              , bookings_source_src_10018.is_instant
              , bookings_source_src_10018.ds
              , DATE_TRUNC('week', bookings_source_src_10018.ds) AS ds__week
              , DATE_TRUNC('month', bookings_source_src_10018.ds) AS ds__month
              , DATE_TRUNC('quarter', bookings_source_src_10018.ds) AS ds__quarter
              , DATE_TRUNC('year', bookings_source_src_10018.ds) AS ds__year
              , bookings_source_src_10018.ds_partitioned
              , DATE_TRUNC('week', bookings_source_src_10018.ds_partitioned) AS ds_partitioned__week
              , DATE_TRUNC('month', bookings_source_src_10018.ds_partitioned) AS ds_partitioned__month
              , DATE_TRUNC('quarter', bookings_source_src_10018.ds_partitioned) AS ds_partitioned__quarter
              , DATE_TRUNC('year', bookings_source_src_10018.ds_partitioned) AS ds_partitioned__year
              , bookings_source_src_10018.booking_paid_at
              , DATE_TRUNC('week', bookings_source_src_10018.booking_paid_at) AS booking_paid_at__week
              , DATE_TRUNC('month', bookings_source_src_10018.booking_paid_at) AS booking_paid_at__month
              , DATE_TRUNC('quarter', bookings_source_src_10018.booking_paid_at) AS booking_paid_at__quarter
              , DATE_TRUNC('year', bookings_source_src_10018.booking_paid_at) AS booking_paid_at__year
              , bookings_source_src_10018.listing_id AS listing
              , bookings_source_src_10018.guest_id AS guest
              , bookings_source_src_10018.host_id AS host
              , bookings_source_src_10018.guest_id AS user
            FROM ***************************.fct_bookings bookings_source_src_10018
          ) subq_0
        ) subq_1
      ) subq_2
      LEFT OUTER JOIN (
        -- Pass Only Elements:
        --   ['user__home_state_latest', 'window_start', 'window_end', 'listing']
        SELECT
          subq_6.window_start
          , subq_6.window_end
          , subq_6.listing
          , subq_6.user__home_state_latest
        FROM (
          -- Join Standard Outputs
          SELECT
            subq_3.window_start AS window_start
            , subq_3.window_start__week AS window_start__week
            , subq_3.window_start__month AS window_start__month
            , subq_3.window_start__quarter AS window_start__quarter
            , subq_3.window_start__year AS window_start__year
            , subq_3.window_end AS window_end
            , subq_3.window_end__week AS window_end__week
            , subq_3.window_end__month AS window_end__month
            , subq_3.window_end__quarter AS window_end__quarter
            , subq_3.window_end__year AS window_end__year
            , subq_3.listing__window_start AS listing__window_start
            , subq_3.listing__window_start__week AS listing__window_start__week
            , subq_3.listing__window_start__month AS listing__window_start__month
            , subq_3.listing__window_start__quarter AS listing__window_start__quarter
            , subq_3.listing__window_start__year AS listing__window_start__year
            , subq_3.listing__window_end AS listing__window_end
            , subq_3.listing__window_end__week AS listing__window_end__week
            , subq_3.listing__window_end__month AS listing__window_end__month
            , subq_3.listing__window_end__quarter AS listing__window_end__quarter
            , subq_3.listing__window_end__year AS listing__window_end__year
            , subq_5.ds AS user__ds
            , subq_5.ds__week AS user__ds__week
            , subq_5.ds__month AS user__ds__month
            , subq_5.ds__quarter AS user__ds__quarter
            , subq_5.ds__year AS user__ds__year
            , subq_3.listing AS listing
            , subq_3.user AS user
            , subq_3.listing__user AS listing__user
            , subq_3.country AS country
            , subq_3.is_lux AS is_lux
            , subq_3.capacity AS capacity
            , subq_3.listing__country AS listing__country
            , subq_3.listing__is_lux AS listing__is_lux
            , subq_3.listing__capacity AS listing__capacity
            , subq_5.home_state_latest AS user__home_state_latest
          FROM (
            -- Read Elements From Data Source 'listings'
            SELECT
              listings_src_10020.active_from AS window_start
              , DATE_TRUNC('week', listings_src_10020.active_from) AS window_start__week
              , DATE_TRUNC('month', listings_src_10020.active_from) AS window_start__month
              , DATE_TRUNC('quarter', listings_src_10020.active_from) AS window_start__quarter
              , DATE_TRUNC('year', listings_src_10020.active_from) AS window_start__year
              , listings_src_10020.active_to AS window_end
              , DATE_TRUNC('week', listings_src_10020.active_to) AS window_end__week
              , DATE_TRUNC('month', listings_src_10020.active_to) AS window_end__month
              , DATE_TRUNC('quarter', listings_src_10020.active_to) AS window_end__quarter
              , DATE_TRUNC('year', listings_src_10020.active_to) AS window_end__year
              , listings_src_10020.country
              , listings_src_10020.is_lux
              , listings_src_10020.capacity
              , listings_src_10020.active_from AS listing__window_start
              , DATE_TRUNC('week', listings_src_10020.active_from) AS listing__window_start__week
              , DATE_TRUNC('month', listings_src_10020.active_from) AS listing__window_start__month
              , DATE_TRUNC('quarter', listings_src_10020.active_from) AS listing__window_start__quarter
              , DATE_TRUNC('year', listings_src_10020.active_from) AS listing__window_start__year
              , listings_src_10020.active_to AS listing__window_end
              , DATE_TRUNC('week', listings_src_10020.active_to) AS listing__window_end__week
              , DATE_TRUNC('month', listings_src_10020.active_to) AS listing__window_end__month
              , DATE_TRUNC('quarter', listings_src_10020.active_to) AS listing__window_end__quarter
              , DATE_TRUNC('year', listings_src_10020.active_to) AS listing__window_end__year
              , listings_src_10020.country AS listing__country
              , listings_src_10020.is_lux AS listing__is_lux
              , listings_src_10020.capacity AS listing__capacity
              , listings_src_10020.listing_id AS listing
              , listings_src_10020.user_id AS user
              , listings_src_10020.user_id AS listing__user
            FROM ***************************.dim_listings listings_src_10020
          ) subq_3
          LEFT OUTER JOIN (
            -- Pass Only Elements:
            --   ['home_state_latest',
            --    'user__home_state_latest',
            --    'ds',
            --    'ds__week',
            --    'ds__month',
            --    'ds__quarter',
            --    'ds__year',
            --    'user__ds',
            --    'user__ds__week',
            --    'user__ds__month',
            --    'user__ds__quarter',
            --    'user__ds__year',
            --    'user']
            SELECT
              subq_4.ds
              , subq_4.ds__week
              , subq_4.ds__month
              , subq_4.ds__quarter
              , subq_4.ds__year
              , subq_4.user__ds
              , subq_4.user__ds__week
              , subq_4.user__ds__month
              , subq_4.user__ds__quarter
              , subq_4.user__ds__year
              , subq_4.user
              , subq_4.home_state_latest
              , subq_4.user__home_state_latest
            FROM (
              -- Read Elements From Data Source 'users_latest'
              SELECT
                users_latest_src_10024.ds
                , DATE_TRUNC('week', users_latest_src_10024.ds) AS ds__week
                , DATE_TRUNC('month', users_latest_src_10024.ds) AS ds__month
                , DATE_TRUNC('quarter', users_latest_src_10024.ds) AS ds__quarter
                , DATE_TRUNC('year', users_latest_src_10024.ds) AS ds__year
                , users_latest_src_10024.home_state_latest
                , users_latest_src_10024.ds AS user__ds
                , DATE_TRUNC('week', users_latest_src_10024.ds) AS user__ds__week
                , DATE_TRUNC('month', users_latest_src_10024.ds) AS user__ds__month
                , DATE_TRUNC('quarter', users_latest_src_10024.ds) AS user__ds__quarter
                , DATE_TRUNC('year', users_latest_src_10024.ds) AS user__ds__year
                , users_latest_src_10024.home_state_latest AS user__home_state_latest
                , users_latest_src_10024.user_id AS user
              FROM ***************************.dim_users_latest users_latest_src_10024
            ) subq_4
          ) subq_5
          ON
            subq_3.user = subq_5.user
        ) subq_6
      ) subq_7
      ON
        (
          subq_2.listing = subq_7.listing
        ) AND (
          (
            subq_2.metric_time >= subq_7.window_start
          ) AND (
            (
              subq_2.metric_time < subq_7.window_end
            ) OR (
              subq_7.window_end IS NULL
            )
          )
        )
    ) subq_8
  ) subq_9
  GROUP BY
    subq_9.metric_time
    , subq_9.listing__user__home_state_latest
) subq_10
