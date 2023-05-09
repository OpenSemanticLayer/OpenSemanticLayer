import pytest

from metricflow.dataset.semantic_model_adapter import DataSourceDataSet
from metricflow.model.semantic_manifest_lookup import SemanticManifestLookup
from metricflow.plan_conversion.column_resolver import DefaultColumnAssociationResolver
from metricflow.plan_conversion.dataflow_to_sql import DataflowToSqlQueryPlanConverter
from metricflow.plan_conversion.time_spine import TimeSpineSource


@pytest.fixture(scope="session")
def dataflow_to_sql_converter(  # noqa: D
    simple_semantic_manifest_lookup: SemanticManifestLookup,
    time_spine_source: TimeSpineSource,
) -> DataflowToSqlQueryPlanConverter[DataSourceDataSet]:
    return DataflowToSqlQueryPlanConverter[DataSourceDataSet](
        column_association_resolver=DefaultColumnAssociationResolver(simple_semantic_manifest_lookup),
        semantic_manifest_lookup=simple_semantic_manifest_lookup,
        time_spine_source=time_spine_source,
    )
