import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  FiActivity,
  FiAlertTriangle,
  FiBarChart2,
  FiCalendar,
  FiDatabase,
  FiGrid,
  FiPercent,
} from 'react-icons/fi'
import CategoryDistributionChart from '../components/charts/CategoryDistributionChart'
import CorrelationHeatmap from '../components/charts/CorrelationHeatmap'
import { formatNumber } from '../components/charts/chartTheme'
import MissingValuesChart from '../components/charts/MissingValuesChart'
import NumericDistributionChart from '../components/charts/NumericDistributionChart'
import OutlierBarChart from '../components/charts/OutlierBarChart'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'
import PageSkeleton from '../components/Skeleton'
import StatCard from '../components/StatCard'
import { useToast } from '../hooks/useToast'
import { useDataset } from '../hooks/useDataset'

function Analytics() {
  const {
    storedFilename,
    analytics,
    loadingAction,
    error,
    clearError,
    fetchAnalytics,
  } = useDataset()
  const toast = useToast()
  const notifiedRef = useRef(null)

  const [numericColumn, setNumericColumn] = useState('')
  const [categoryColumn, setCategoryColumn] = useState('')

  const requestAnalytics = useCallback(
    async ({ notify = false, signal } = {}) => {
      if (!storedFilename) return
      clearError()
      try {
        await fetchAnalytics(storedFilename, { signal })
        if (signal?.aborted) return
        if (notify || notifiedRef.current !== storedFilename) {
          toast.success('Analytics completed successfully.')
          notifiedRef.current = storedFilename
        }
      } catch (err) {
        if (err?.error === 'REQUEST_CANCELLED' || signal?.aborted) return
        notifiedRef.current = null
      }
    },
    [storedFilename, clearError, fetchAnalytics, toast],
  )

  useEffect(() => {
    if (!storedFilename) return undefined
    if (analytics?.stored_filename === storedFilename) return undefined

    const controller = new AbortController()
    void requestAnalytics({ notify: true, signal: controller.signal })
    return () => {
      controller.abort()
    }
  }, [storedFilename, analytics?.stored_filename, requestAnalytics])

  const matches = analytics?.stored_filename === storedFilename
  const visibleError =
    error &&
    error.error !== 'REQUEST_CANCELLED' &&
    error.error !== 'REQUEST_IN_FLIGHT'
      ? error
      : null
  const showLoader = !matches && loadingAction === 'analytics'

  const numericColumns = useMemo(
    () => (matches ? analytics.dataset_summary?.numeric_columns || [] : []),
    [matches, analytics],
  )
  const categoricalColumns = useMemo(
    () => (matches ? analytics.dataset_summary?.categorical_columns || [] : []),
    [matches, analytics],
  )
  const summary = matches ? analytics.dataset_summary : null

  const selectedNumeric = numericColumns.includes(numericColumn)
    ? numericColumn
    : numericColumns[0] || ''
  const selectedCategory = categoricalColumns.includes(categoryColumn)
    ? categoryColumn
    : categoricalColumns[0] || ''

  const numericStatRows = useMemo(() => {
    if (!matches) return []
    const stats = analytics.numeric_statistics || {}
    return Object.entries(stats).map(([column, values]) => ({
      column,
      mean: values.mean,
      median: values.median,
      mode: values.mode,
      std: values.standard_deviation,
      variance: values.variance,
      min: values.min,
      max: values.max,
      skewness: values.skewness,
      kurtosis: values.kurtosis,
    }))
  }, [analytics, matches])

  const outlierRows = useMemo(() => {
    if (!matches) return []
    const outliers = analytics.outlier_detection || {}
    return Object.entries(outliers).map(([column, result]) => ({
      column,
      method: result.method,
      lower_bound: result.lower_bound,
      upper_bound: result.upper_bound,
      outlier_count: result.outlier_count,
    }))
  }, [analytics, matches])

  const outlierChartData = useMemo(
    () =>
      outlierRows.map((row) => ({
        column: row.column,
        outlier_count: row.outlier_count || 0,
      })),
    [outlierRows],
  )

  const datetimeRows = useMemo(() => {
    if (!matches) return []
    const stats = analytics.datetime_statistics || {}
    return Object.entries(stats).map(([column, values]) => ({
      column,
      min_date: values.min_date,
      max_date: values.max_date,
      date_range: values.date_range,
    }))
  }, [analytics, matches])

  const categoryFrequencies = useMemo(() => {
    if (!matches || !selectedCategory) return []
    const stats = analytics.categorical_statistics?.[selectedCategory]
    if (!stats) return []
    const frequencies = stats.frequencies || stats.top_values || []
    return frequencies.slice(0, 12).map((item) => ({
      value: String(item.value),
      frequency: item.frequency,
    }))
  }, [analytics, matches, selectedCategory])

  const numericStatColumns = [
    { key: 'column', label: 'Column' },
    { key: 'mean', label: 'Mean', render: (v) => formatNumber(v) },
    { key: 'median', label: 'Median', render: (v) => formatNumber(v) },
    { key: 'mode', label: 'Mode', render: (v) => formatNumber(v) },
    { key: 'std', label: 'Std Dev', render: (v) => formatNumber(v) },
    { key: 'variance', label: 'Variance', render: (v) => formatNumber(v) },
    { key: 'min', label: 'Min', render: (v) => formatNumber(v) },
    { key: 'max', label: 'Max', render: (v) => formatNumber(v) },
    { key: 'skewness', label: 'Skew', render: (v) => formatNumber(v) },
    { key: 'kurtosis', label: 'Kurtosis', render: (v) => formatNumber(v) },
  ]

  const outlierColumns = [
    { key: 'column', label: 'Column' },
    { key: 'method', label: 'Method' },
    { key: 'lower_bound', label: 'Lower', render: (v) => formatNumber(v) },
    { key: 'upper_bound', label: 'Upper', render: (v) => formatNumber(v) },
    {
      key: 'outlier_count',
      label: 'Outliers',
      render: (v) => formatNumber(v, 0),
    },
  ]

  const datetimeColumnsDef = [
    { key: 'column', label: 'Column' },
    { key: 'min_date', label: 'Min date' },
    { key: 'max_date', label: 'Max date' },
    {
      key: 'date_range',
      label: 'Range (days)',
      render: (v) => formatNumber(v, 0),
    },
  ]

  if (!storedFilename) {
    return (
      <div className="page analytics-page">
        <header className="page__header">
          <span className="page__eyebrow">Insights</span>
          <h2 className="page__heading">Analytics</h2>
          <p className="page__description">
            Statistical analysis, correlations, outliers, and distributions.
          </p>
        </header>
        <EmptyState
          icon={FiBarChart2}
          title="No dataset selected"
          text="Upload a dataset first, then open Analytics to explore statistics and charts."
        />
      </div>
    )
  }

  return (
    <div className="page analytics-page">
      <header className="page__header">
        <span className="page__eyebrow">Insights</span>
        <h2 className="page__heading">Analytics</h2>
        <p className="page__description">
          Explore summary metrics, correlations, distributions, and outliers for the
          active dataset.
        </p>
      </header>

      {visibleError ? (
        <ErrorAlert
          error={visibleError}
          title="Analytics request failed"
          onDismiss={clearError}
          onRetry={() => requestAnalytics({ notify: true })}
          retryLabel="Retry analytics"
          retryDisabled={loadingAction === 'analytics'}
        />
      ) : null}

      {showLoader ? (
        <PageSkeleton cards={4} label="Running analytics…" />
      ) : matches ? (
        <>
          <section className="kpi-grid" aria-label="Dataset summary">
            <StatCard
              label="Rows"
              value={formatNumber(summary.rows, 0)}
              hint="Dataset rows"
              icon={FiDatabase}
              tone="primary"
            />
            <StatCard
              label="Columns"
              value={formatNumber(summary.columns, 0)}
              hint={`${numericColumns.length} numeric · ${categoricalColumns.length} categorical`}
              icon={FiGrid}
              tone="accent"
            />
            <StatCard
              label="Missing Cells"
              value={formatNumber(analytics.missing_values?.count, 0)}
              hint={`${formatNumber(analytics.missing_values?.percentage)}% of cells`}
              icon={FiPercent}
              tone="warning"
            />
            <StatCard
              label="Datetime Fields"
              value={formatNumber(summary.datetime_columns?.length || 0, 0)}
              hint="Temporal columns detected"
              icon={FiCalendar}
              tone="success"
            />
          </section>

          <div className="analytics-grid">
            <ChartCard
              title="Missing Value Summary"
              subtitle="Present vs missing cells across the dataset"
            >
              <MissingValuesChart
                count={analytics.missing_values?.count || 0}
                percentage={analytics.missing_values?.percentage || 0}
                totalCells={
                  summary.rows && summary.columns
                    ? summary.rows * summary.columns
                    : null
                }
              />
            </ChartCard>

            <ChartCard
              title="Correlation Matrix"
              subtitle="Pearson correlation across numeric columns"
            >
              <CorrelationHeatmap
                columns={analytics.correlation_matrix?.columns || []}
                values={analytics.correlation_matrix?.values || []}
              />
            </ChartCard>
          </div>

          <ChartCard
            title="Numerical Statistics"
            subtitle="Mean, median, variance, skewness, and related metrics"
          >
            <DataTable
              columns={numericStatColumns}
              rows={numericStatRows}
              emptyMessage="No numeric statistics available for this dataset."
            />
          </ChartCard>

          <div className="analytics-grid">
            <ChartCard
              title="Distribution Charts"
              subtitle="Summary distribution from backend numeric statistics"
              actions={
                numericColumns.length ? (
                  <label className="chart-select">
                    <span className="visually-hidden">Numeric column</span>
                    <select
                      value={selectedNumeric}
                      onChange={(event) => setNumericColumn(event.target.value)}
                    >
                      {numericColumns.map((column) => (
                        <option key={column} value={column}>
                          {column}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null
              }
              empty={
                numericColumns.length
                  ? null
                  : 'No numeric columns available for distribution charts.'
              }
            >
              {selectedNumeric ? (
                <NumericDistributionChart
                  stats={analytics.numeric_statistics?.[selectedNumeric]}
                />
              ) : null}
            </ChartCard>

            <ChartCard
              title="Category Charts"
              subtitle="Top category frequencies"
              actions={
                categoricalColumns.length ? (
                  <label className="chart-select">
                    <span className="visually-hidden">Categorical column</span>
                    <select
                      value={selectedCategory}
                      onChange={(event) => setCategoryColumn(event.target.value)}
                    >
                      {categoricalColumns.map((column) => (
                        <option key={column} value={column}>
                          {column}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null
              }
              empty={
                categoricalColumns.length
                  ? null
                  : 'No categorical columns available for category charts.'
              }
            >
              {selectedCategory ? (
                <CategoryDistributionChart data={categoryFrequencies} />
              ) : null}
            </ChartCard>
          </div>

          <div className="analytics-grid">
            <ChartCard
              title="Outlier Summary"
              subtitle="IQR outlier counts by numeric column"
            >
              <OutlierBarChart data={outlierChartData} />
            </ChartCard>

            <ChartCard
              title="Outlier Details"
              subtitle="Bounds and outlier counts"
            >
              <DataTable
                columns={outlierColumns}
                rows={outlierRows}
                emptyMessage="No outlier detection results available."
              />
            </ChartCard>
          </div>

          <ChartCard
            title="Date/Time Analysis"
            subtitle={
              datetimeRows.length
                ? 'Min/max dates and range in days'
                : 'No datetime columns detected in this dataset'
            }
            empty={
              datetimeRows.length
                ? null
                : 'Datetime analysis is unavailable because no datetime columns were found.'
            }
          >
            {datetimeRows.length ? (
              <DataTable columns={datetimeColumnsDef} rows={datetimeRows} />
            ) : null}
          </ChartCard>

          <section className="overview-panel">
            <div className="overview-panel__header">
              <h3 className="overview-panel__title">
                <FiActivity aria-hidden="true" /> Column inventory
              </h3>
              <p className="overview-panel__subtitle">
                Numeric, categorical, and datetime fields returned by analytics.
              </p>
            </div>
            <div className="type-chip-row">
              {numericColumns.map((column) => (
                <span key={`n-${column}`} className="type-chip type-chip--numeric">
                  {column}
                </span>
              ))}
              {categoricalColumns.map((column) => (
                <span key={`c-${column}`} className="type-chip type-chip--categorical">
                  {column}
                </span>
              ))}
              {(summary.datetime_columns || []).map((column) => (
                <span key={`d-${column}`} className="type-chip type-chip--datetime">
                  {column}
                </span>
              ))}
            </div>
          </section>
        </>
      ) : !showLoader ? (
        <EmptyState
          icon={FiAlertTriangle}
          title="Analytics unavailable"
          text="The analytics endpoint did not return data for this file."
          actionLabel="Retry analytics"
          onAction={() => requestAnalytics({ notify: true })}
          actionDisabled={loadingAction === 'analytics'}
        />
      ) : null}
    </div>
  )
}

export default Analytics
