import { useEffect, useMemo } from 'react'
import {
  FiAlertTriangle,
  FiCheckCircle,
  FiShield,
  FiXCircle,
} from 'react-icons/fi'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'
import Loader from '../components/Loader'
import StatCard from '../components/StatCard'
import { useDataset } from '../hooks/useDataset'

function formatScore(value) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return Number(value).toFixed(1)
}

function SeverityBadge({ severity }) {
  const normalized = String(severity || 'info').toLowerCase()
  return (
    <span className={`severity-badge severity-badge--${normalized}`}>
      {normalized}
    </span>
  )
}

function StatusBadge({ passed }) {
  return (
    <span className={`status-badge status-badge--${passed ? 'pass' : 'fail'}`}>
      {passed ? 'Passed' : 'Failed'}
    </span>
  )
}

function buildRecommendations(failedRules = [], report = {}) {
  const recommendations = []

  for (const rule of failedRules) {
    const columnPart = rule.column ? `Column "${rule.column}": ` : ''
    recommendations.push({
      id: rule.rule_id,
      severity: rule.severity || 'warning',
      text: `${columnPart}${rule.message || rule.description}`,
    })
  }

  const criticalCount = (report.critical_failures || []).length
  if (criticalCount > 0) {
    recommendations.unshift({
      id: 'critical-priority',
      severity: 'critical',
      text: `Resolve ${criticalCount} critical failure${criticalCount === 1 ? '' : 's'} before loading to the warehouse.`,
    })
  }

  if (!recommendations.length) {
    recommendations.push({
      id: 'all-clear',
      severity: 'info',
      text: 'All evaluated rules passed. Dataset looks ready for downstream analytics and warehouse load.',
    })
  }

  return recommendations
}

function Quality() {
  const {
    storedFilename,
    quality,
    loading,
    error,
    clearError,
    fetchQuality,
  } = useDataset()

  useEffect(() => {
    if (!storedFilename) return undefined

    const load = async () => {
      try {
        await fetchQuality(storedFilename)
      } catch {
        // Error lives in DatasetContext.
      }
    }

    void load()
    return undefined
  }, [storedFilename, fetchQuality])

  const matches = quality?.stored_filename === storedFilename
  const summary = matches ? quality.validation_summary : null
  const report = useMemo(
    () => (matches ? quality.validation_report || {} : {}),
    [matches, quality],
  )

  const severityCounts = useMemo(() => {
    if (!matches) {
      return { critical: 0, warning: 0, info: 0 }
    }
    const allRules = [...(quality.passed_rules || []), ...(quality.failed_rules || [])]
    return allRules.reduce(
      (acc, rule) => {
        const key = String(rule.severity || 'info').toLowerCase()
        if (key === 'critical') acc.critical += 1
        else if (key === 'warning') acc.warning += 1
        else acc.info += 1
        return acc
      },
      { critical: 0, warning: 0, info: 0 },
    )
  }, [matches, quality])

  const recommendations = useMemo(() => {
    if (!matches) return []
    return buildRecommendations(quality.failed_rules || [], report)
  }, [matches, quality, report])

  const ruleColumns = [
    { key: 'rule_id', label: 'Rule ID' },
    { key: 'rule_type', label: 'Type' },
    { key: 'column', label: 'Column', render: (v) => v || '—' },
    {
      key: 'severity',
      label: 'Severity',
      render: (value) => <SeverityBadge severity={value} />,
    },
    {
      key: 'passed',
      label: 'Status',
      render: (value) => <StatusBadge passed={Boolean(value)} />,
    },
    { key: 'description', label: 'Description' },
    { key: 'message', label: 'Message' },
  ]

  if (!storedFilename) {
    return (
      <div className="page quality-page">
        <header className="page__header">
          <span className="page__eyebrow">Validation</span>
          <h2 className="page__heading">Data Quality</h2>
          <p className="page__description">
            Run rule-based validation for nulls, duplicates, types, ranges, and more.
          </p>
        </header>
        <EmptyState
          icon={FiShield}
          title="No dataset selected"
          text="Upload a dataset first, then open Data Quality to run validation checks."
        />
      </div>
    )
  }

  const showLoader = loading && !matches

  return (
    <div className="page quality-page">
      <header className="page__header">
        <span className="page__eyebrow">Validation</span>
        <h2 className="page__heading">Data Quality</h2>
        <p className="page__description">
          Weighted quality score, passed and failed rules, severity breakdown, and
          recommended next actions.
        </p>
      </header>

      {error ? (
        <ErrorAlert
          error={error}
          title="Quality check failed"
          onDismiss={clearError}
        />
      ) : null}

      {showLoader ? (
        <Loader fullPage label="Running quality checks…" />
      ) : matches ? (
        <>
          <section className="kpi-grid" aria-label="Quality summary">
            <StatCard
              label="Quality Score"
              value={formatScore(summary.quality_score)}
              hint="Weighted score out of 100"
              icon={FiShield}
              tone="primary"
            />
            <StatCard
              label="Passed Rules"
              value={String(summary.passed_rules ?? 0)}
              hint="Rules that passed validation"
              icon={FiCheckCircle}
              tone="success"
            />
            <StatCard
              label="Failed Rules"
              value={String(summary.failed_rules ?? 0)}
              hint="Rules that failed validation"
              icon={FiXCircle}
              tone="warning"
            />
            <StatCard
              label="Total Rules"
              value={String(summary.total_rules ?? 0)}
              hint="Rules evaluated for this dataset"
              icon={FiAlertTriangle}
              tone="accent"
            />
          </section>

          <section className="kpi-grid kpi-grid--three" aria-label="Severity levels">
            <StatCard
              label="Critical"
              value={String(severityCounts.critical)}
              hint="Highest severity rules"
              tone="warning"
            />
            <StatCard
              label="Warning"
              value={String(severityCounts.warning)}
              hint="Medium severity rules"
              tone="accent"
            />
            <StatCard
              label="Info"
              value={String(severityCounts.info)}
              hint="Informational rules"
              tone="primary"
            />
          </section>

          <ChartCard
            title="Recommendations"
            subtitle="Suggested actions based on failed rules and severity"
          >
            <ul className="recommendation-list">
              {recommendations.map((item) => (
                <li
                  key={item.id}
                  className={`recommendation-list__item recommendation-list__item--${item.severity}`}
                >
                  <SeverityBadge severity={item.severity} />
                  <p>{item.text}</p>
                </li>
              ))}
            </ul>
          </ChartCard>

          <ChartCard
            title="Passed Rules"
            subtitle={`${quality.passed_rules?.length || 0} rules passed`}
          >
            <DataTable
              columns={ruleColumns}
              rows={quality.passed_rules || []}
              emptyMessage="No passed rules to display."
            />
          </ChartCard>

          <ChartCard
            title="Failed Rules"
            subtitle={`${quality.failed_rules?.length || 0} rules failed`}
          >
            <DataTable
              columns={ruleColumns}
              rows={quality.failed_rules || []}
              emptyMessage="No failed rules. Dataset passed all quality checks."
            />
          </ChartCard>

          <section className="overview-panel">
            <div className="overview-panel__header">
              <h3 className="overview-panel__title">Validation report</h3>
              <p className="overview-panel__subtitle">
                Dataset shape and rule types evaluated by the quality engine.
              </p>
            </div>
            <div className="quality-report-grid">
              <div>
                <span className="quality-report-grid__label">Rows</span>
                <strong>{report.dataset_rows ?? '—'}</strong>
              </div>
              <div>
                <span className="quality-report-grid__label">Columns</span>
                <strong>{report.dataset_columns ?? '—'}</strong>
              </div>
              <div className="quality-report-grid__span">
                <span className="quality-report-grid__label">Rule types</span>
                <div className="type-chip-row">
                  {(report.rule_types_evaluated || []).length ? (
                    report.rule_types_evaluated.map((type) => (
                      <span key={type} className="type-chip">
                        {type}
                      </span>
                    ))
                  ) : (
                    <span className="overview-panel__subtitle">None reported</span>
                  )}
                </div>
              </div>
            </div>
          </section>
        </>
      ) : !loading ? (
        <EmptyState
          icon={FiAlertTriangle}
          title="Quality results unavailable"
          text="The quality-check endpoint did not return data for this file."
        />
      ) : null}
    </div>
  )
}

export default Quality
