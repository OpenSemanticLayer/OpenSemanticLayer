from metricflow.sql.render.expr_renderer import (
    DefaultSqlExpressionRenderer,
    SqlExpressionRenderer,
    SqlExpressionRenderResult,
)
from metricflow.sql.render.sql_plan_renderer import DefaultSqlQueryPlanRenderer
from metricflow.sql.sql_bind_parameters import SqlBindParameters
from metricflow.sql.sql_exprs import (
    SqlCastToTimestampExpression,
    SqlDateTruncExpression,
    SqlGenerateUuidExpression,
    SqlPercentileExpression,
    SqlTimeDeltaExpression,
)
from metricflow.time.time_granularity import TimeGranularity


class BigQuerySqlExpressionRenderer(DefaultSqlExpressionRenderer):
    """Expression renderer for the BigQuery engine."""

    @property
    def double_data_type(self) -> str:
        """Custom double data type for BigQuery engine"""
        return "FLOAT64"

    def visit_percentile_expr(self, node: SqlPercentileExpression) -> SqlExpressionRenderResult:
        """Render a percentile expression"""
        arg_rendered = self.render_sql_expr(node.order_by_arg)
        params = arg_rendered.execution_parameters

        function_str = node.percentile_args.function_name
        percentile = node.percentile_args.percentile

        return SqlExpressionRenderResult(
            sql=f"{function_str}({arg_rendered.sql}, {percentile}) OVER()",
            execution_parameters=params,
        )

    def visit_cast_to_timestamp_expr(self, node: SqlCastToTimestampExpression) -> SqlExpressionRenderResult:
        """Casts the time value expression to DATETIME, as per standard BigQuery preferences."""
        arg_rendered = self.render_sql_expr(node.arg)
        return SqlExpressionRenderResult(
            sql=f"CAST({arg_rendered.sql} AS DATETIME)",
            execution_parameters=arg_rendered.execution_parameters,
        )

    def visit_date_trunc_expr(self, node: SqlDateTruncExpression) -> SqlExpressionRenderResult:
        """Render DATE_TRUNC for BigQuery, which takes the opposite argument order from Snowflake and Redshift"""
        arg_rendered = self.render_sql_expr(node.arg)

        prefix = ""
        if node.time_granularity in (TimeGranularity.WEEK, TimeGranularity.YEAR):
            prefix = "iso"

        return SqlExpressionRenderResult(
            sql=f"DATE_TRUNC({arg_rendered.sql}, {prefix}{node.time_granularity.value})",
            execution_parameters=arg_rendered.execution_parameters,
        )

    def visit_time_delta_expr(self, node: SqlTimeDeltaExpression) -> SqlExpressionRenderResult:  # noqa: D
        column = node.arg.accept(self)
        if node.grain_to_date:
            granularity = node.granularity
            if granularity == TimeGranularity.WEEK or granularity == TimeGranularity.YEAR:
                granularity.value = "ISO" + granularity.value.upper()
            return SqlExpressionRenderResult(
                sql=f"DATE_TRUNC({column.sql}, {granularity.value})",
                execution_parameters=column.execution_parameters,
            )

        return SqlExpressionRenderResult(
            sql=f"DATE_SUB(CAST({column.sql} AS DATETIME), INTERVAL {node.count} {node.granularity.value})",
            execution_parameters=column.execution_parameters,
        )

    def visit_generate_uuid_expr(self, node: SqlGenerateUuidExpression) -> SqlExpressionRenderResult:  # noqa: D
        return SqlExpressionRenderResult(
            sql="GENERATE_UUID()",
            execution_parameters=SqlBindParameters(),
        )


class BigQuerySqlQueryPlanRenderer(DefaultSqlQueryPlanRenderer):
    """Plan renderer for the BigQuery engine."""

    EXPR_RENDERER = BigQuerySqlExpressionRenderer()

    @property
    def expr_renderer(self) -> SqlExpressionRenderer:  # noqa :D
        return self.EXPR_RENDERER
