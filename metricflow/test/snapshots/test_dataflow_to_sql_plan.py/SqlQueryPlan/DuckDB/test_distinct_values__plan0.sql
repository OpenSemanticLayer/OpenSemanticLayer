-- Order By ['listing__country_latest'] Limit 100
SELECT
  subq_2.listing__country_latest
FROM (
  -- Constrain Output with WHERE
  SELECT
    subq_1.listing__country_latest
  FROM (
    -- Pass Only Elements:
    --   ['listing__country_latest']
    SELECT
      subq_0.listing__country_latest
    FROM (
      -- Read Elements From Semantic Model 'listings_latest'
      SELECT
        1 AS listings
        , listings_latest_src_10004.capacity AS largest_listing
        , listings_latest_src_10004.capacity AS smallest_listing
        , listings_latest_src_10004.created_at AS ds__day
        , DATE_TRUNC('week', listings_latest_src_10004.created_at) AS ds__week
        , DATE_TRUNC('month', listings_latest_src_10004.created_at) AS ds__month
        , DATE_TRUNC('quarter', listings_latest_src_10004.created_at) AS ds__quarter
        , DATE_TRUNC('year', listings_latest_src_10004.created_at) AS ds__year
        , listings_latest_src_10004.created_at AS created_at__day
        , DATE_TRUNC('week', listings_latest_src_10004.created_at) AS created_at__week
        , DATE_TRUNC('month', listings_latest_src_10004.created_at) AS created_at__month
        , DATE_TRUNC('quarter', listings_latest_src_10004.created_at) AS created_at__quarter
        , DATE_TRUNC('year', listings_latest_src_10004.created_at) AS created_at__year
        , listings_latest_src_10004.country AS country_latest
        , listings_latest_src_10004.is_lux AS is_lux_latest
        , listings_latest_src_10004.capacity AS capacity_latest
        , listings_latest_src_10004.created_at AS listing__ds__day
        , DATE_TRUNC('week', listings_latest_src_10004.created_at) AS listing__ds__week
        , DATE_TRUNC('month', listings_latest_src_10004.created_at) AS listing__ds__month
        , DATE_TRUNC('quarter', listings_latest_src_10004.created_at) AS listing__ds__quarter
        , DATE_TRUNC('year', listings_latest_src_10004.created_at) AS listing__ds__year
        , listings_latest_src_10004.created_at AS listing__created_at__day
        , DATE_TRUNC('week', listings_latest_src_10004.created_at) AS listing__created_at__week
        , DATE_TRUNC('month', listings_latest_src_10004.created_at) AS listing__created_at__month
        , DATE_TRUNC('quarter', listings_latest_src_10004.created_at) AS listing__created_at__quarter
        , DATE_TRUNC('year', listings_latest_src_10004.created_at) AS listing__created_at__year
        , listings_latest_src_10004.country AS listing__country_latest
        , listings_latest_src_10004.is_lux AS listing__is_lux_latest
        , listings_latest_src_10004.capacity AS listing__capacity_latest
        , listings_latest_src_10004.listing_id AS listing
        , listings_latest_src_10004.user_id AS user
        , listings_latest_src_10004.user_id AS listing__user
      FROM ***************************.dim_listings_latest listings_latest_src_10004
    ) subq_0
    GROUP BY
      subq_0.listing__country_latest
  ) subq_1
  WHERE listing__country_latest = 'us'
) subq_2
ORDER BY subq_2.listing__country_latest DESC
LIMIT 100
