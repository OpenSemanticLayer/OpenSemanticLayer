import logging

from _pytest.fixtures import FixtureRequest

from metricflow.instances import DataSourceReference
from metricflow.protocols.sql_client import SqlClient
from metricflow.specs import (
    DimensionSpec,
    IdentifierSpec,
    InstanceSpecSet,
    MeasureSpec,
    TimeDimensionSpec,
    IdentifierReference,
)
from metricflow.sql.render.sql_plan_renderer import SqlQueryPlanRenderer
from metricflow.test.fixtures.model_fixtures import ConsistentIdObjectRepository
from metricflow.test.fixtures.setup_fixtures import MetricFlowTestSessionState
from metricflow.test.sql.compare_sql_plan import assert_rendered_sql_equal
from metricflow.time.time_granularity import TimeGranularity

logger = logging.getLogger(__name__)


def test_convert_table_data_source_without_measures(  # noqa: D
    request: FixtureRequest,
    mf_test_session_state: MetricFlowTestSessionState,
    sql_client: SqlClient,
    consistent_id_object_repository: ConsistentIdObjectRepository,
) -> None:
    """Simple test for converting a table data source. Since there are no measures, primary time is not checked."""
    users_data_set = consistent_id_object_repository.simple_model_data_sets["users_latest"]

    expected_spec_set = InstanceSpecSet(
        metric_specs=(),
        measure_specs=(),
        dimension_specs=(
            DimensionSpec(element_name="home_state_latest", identifier_links=()),
            DimensionSpec(
                element_name="home_state_latest",
                identifier_links=(IdentifierReference(element_name="user"),),
            ),
        ),
        identifier_specs=(IdentifierSpec(element_name="user", identifier_links=()),),
        time_dimension_specs=(
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.DAY),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.WEEK),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.MONTH),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.QUARTER),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.YEAR),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="user"),),
                time_granularity=TimeGranularity.DAY,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="user"),),
                time_granularity=TimeGranularity.WEEK,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="user"),),
                time_granularity=TimeGranularity.MONTH,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="user"),),
                time_granularity=TimeGranularity.QUARTER,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="user"),),
                time_granularity=TimeGranularity.YEAR,
            ),
        ),
    )

    assert users_data_set.instance_set.spec_set == expected_spec_set
    assert users_data_set.data_source_reference == DataSourceReference(data_source_name="users_latest")
    assert_rendered_sql_equal(
        request=request,
        mf_test_session_state=mf_test_session_state,
        plan_id="plan0",
        select_node=users_data_set.sql_select_node,
        sql_client=sql_client,
    )


def test_convert_table_data_source_with_measures(  # noqa: D
    request: FixtureRequest,
    mf_test_session_state: MetricFlowTestSessionState,
    sql_client: SqlClient,
    consistent_id_object_repository: ConsistentIdObjectRepository,
) -> None:
    """Complete test of table data source conversion. This includes the full set of measures/identifiers/dimensions.

    Measures trigger a primary time dimension validation. Additionally, this includes both categorical and time
    dimension types, which should cover most, if not all, of the table source branches in the target class.
    """
    id_verifications_data_set = consistent_id_object_repository.simple_model_data_sets["id_verifications"]

    expected_spec_set = InstanceSpecSet(
        metric_specs=(),
        measure_specs=(MeasureSpec(element_name="identity_verifications"),),
        dimension_specs=(
            DimensionSpec(element_name="verification_type", identifier_links=()),
            DimensionSpec(
                element_name="verification_type",
                identifier_links=(IdentifierReference(element_name="verification"),),
            ),
        ),
        identifier_specs=(
            IdentifierSpec(element_name="verification", identifier_links=()),
            IdentifierSpec(element_name="user", identifier_links=()),
            IdentifierSpec(
                element_name="user",
                identifier_links=(IdentifierReference(element_name="verification"),),
            ),
        ),
        time_dimension_specs=(
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.DAY),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.WEEK),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.MONTH),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.QUARTER),
            TimeDimensionSpec(element_name="ds", identifier_links=(), time_granularity=TimeGranularity.YEAR),
            TimeDimensionSpec(element_name="ds_partitioned", identifier_links=(), time_granularity=TimeGranularity.DAY),
            TimeDimensionSpec(
                element_name="ds_partitioned", identifier_links=(), time_granularity=TimeGranularity.WEEK
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned", identifier_links=(), time_granularity=TimeGranularity.MONTH
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned", identifier_links=(), time_granularity=TimeGranularity.QUARTER
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned", identifier_links=(), time_granularity=TimeGranularity.YEAR
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.DAY,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.WEEK,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.MONTH,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.QUARTER,
            ),
            TimeDimensionSpec(
                element_name="ds",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.YEAR,
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.DAY,
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.WEEK,
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.MONTH,
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.QUARTER,
            ),
            TimeDimensionSpec(
                element_name="ds_partitioned",
                identifier_links=(IdentifierReference(element_name="verification"),),
                time_granularity=TimeGranularity.YEAR,
            ),
        ),
    )

    assert id_verifications_data_set.instance_set.spec_set == expected_spec_set
    assert id_verifications_data_set.data_source_reference == DataSourceReference(data_source_name="id_verifications")
    assert_rendered_sql_equal(
        request=request,
        mf_test_session_state=mf_test_session_state,
        plan_id="plan0",
        select_node=id_verifications_data_set.sql_select_node,
        sql_client=sql_client,
    )


def test_convert_query_data_source(  # noqa: D
    request: FixtureRequest,
    mf_test_session_state: MetricFlowTestSessionState,
    sql_client: SqlClient,
    default_sql_plan_renderer: SqlQueryPlanRenderer,
    consistent_id_object_repository: ConsistentIdObjectRepository,
) -> None:
    bookings_data_set = consistent_id_object_repository.simple_model_data_sets["revenue"]

    assert_rendered_sql_equal(
        request=request,
        mf_test_session_state=mf_test_session_state,
        plan_id="plan0",
        select_node=bookings_data_set.sql_select_node,
        sql_client=sql_client,
    )
