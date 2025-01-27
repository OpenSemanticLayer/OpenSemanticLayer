import pytest

from metricflow.dataflow.dataflow_plan import ValidityWindowJoinDescription
from metricflow.instances import InstanceSet
from metricflow.model.semantic_model import SemanticModel
from metricflow.plan_conversion.instance_converters import CreateValidityWindowJoinDescription
from metricflow.specs import TimeDimensionSpec
from metricflow.test.fixtures.model_fixtures import ConsistentIdObjectRepository
from metricflow.time.time_granularity import TimeGranularity


def test_no_validity_dims(
    consistent_id_object_repository: ConsistentIdObjectRepository, scd_semantic_model: SemanticModel
) -> None:
    """Tests converting an instance set with no matching dimensions to a ValidityWindowJoinDescription"""
    # bookings_source is a fact table, and has no validity window dimensions
    dataset = consistent_id_object_repository.scd_model_data_sets["bookings_source"]

    validity_window_join_description = CreateValidityWindowJoinDescription(
        data_source_semantics=scd_semantic_model.data_source_semantics
    ).transform(instance_set=dataset.instance_set)

    assert validity_window_join_description is None, (
        f"We managed to create a validity window join description `{validity_window_join_description}` from a "
        f"data source that does not have one defined!"
    )


def test_validity_window_conversion(
    consistent_id_object_repository: ConsistentIdObjectRepository, scd_semantic_model: SemanticModel
) -> None:
    """Tests converting an instance set with a single validity window into a ValidityWindowJoinDescription"""
    # The listings data source uses a 2-column SCD Type III layout
    dataset = consistent_id_object_repository.scd_model_data_sets["listings"]
    expected_join_description = ValidityWindowJoinDescription(
        window_start_dimension=TimeDimensionSpec(
            element_name="window_start",
            time_granularity=TimeGranularity.DAY,
            identifier_links=(),
        ),
        window_end_dimension=TimeDimensionSpec(
            element_name="window_end", time_granularity=TimeGranularity.DAY, identifier_links=()
        ),
    )

    validity_window_join_description = CreateValidityWindowJoinDescription(
        data_source_semantics=scd_semantic_model.data_source_semantics
    ).transform(instance_set=dataset.instance_set)

    assert (
        validity_window_join_description is not None
    ), "Failed to make a validity window join description from a dataset which should have one configured!"
    assert (
        validity_window_join_description == expected_join_description
    ), f"Expected validity window: `{expected_join_description}` but got: `{validity_window_join_description}`"


def test_multiple_validity_windows(
    consistent_id_object_repository: ConsistentIdObjectRepository, scd_semantic_model: SemanticModel
) -> None:
    """Tests the behavior of this converter when it encounters an instance set with multiple validity windows"""
    first_dataset = consistent_id_object_repository.scd_model_data_sets["listings"]
    second_dataset = consistent_id_object_repository.scd_model_data_sets["primary_accounts"]
    merged_instance_set = InstanceSet.merge([first_dataset.instance_set, second_dataset.instance_set])
    with pytest.raises(AssertionError, match="Found more than 1 set of validity window specs"):
        CreateValidityWindowJoinDescription(data_source_semantics=scd_semantic_model.data_source_semantics).transform(
            merged_instance_set
        )
