import { useHealthCheck } from '../hooks/useHealthCheck'
import { HealthContext } from './health-context'

/**
 * Single shared health poller for the app shell (navbar + settings).
 * Avoids duplicate /health requests from multiple useHealthCheck() mounts.
 */
export function HealthProvider({ children }) {
  const health = useHealthCheck()
  return <HealthContext.Provider value={health}>{children}</HealthContext.Provider>
}

export default HealthProvider
