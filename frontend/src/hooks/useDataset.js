import { useContext } from 'react'
import { DatasetContext } from '../context/dataset-context'

/**
 * Access shared dataset state and API actions from DatasetContext.
 */
export function useDataset() {
  const context = useContext(DatasetContext)
  if (!context) {
    throw new Error('useDataset must be used within a DatasetProvider')
  }
  return context
}

export default useDataset
