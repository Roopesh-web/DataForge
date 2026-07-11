import { useCallback, useId, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiFile, FiUploadCloud, FiX } from 'react-icons/fi'
import Toast from '../components/Toast'
import { useDataset } from '../hooks/useDataset'

const ACCEPTED_EXTENSIONS = ['.csv', '.xlsx', '.json']
const ACCEPT_ATTR = '.csv,.xlsx,.json,text/csv,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

function formatFileSize(bytes) {
  if (!Number.isFinite(bytes) || bytes < 0) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function getExtension(filename = '') {
  const parts = filename.toLowerCase().split('.')
  if (parts.length < 2) return ''
  return `.${parts.at(-1)}`
}

function isAcceptedFile(file) {
  if (!file?.name) return false
  return ACCEPTED_EXTENSIONS.includes(getExtension(file.name))
}

function Upload() {
  const inputId = useId()
  const inputRef = useRef(null)
  const navigate = useNavigate()
  const { uploadDataset, clearError } = useDataset()

  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [validationError, setValidationError] = useState(null)
  const [toast, setToast] = useState(null)

  const showToast = useCallback((type, message) => {
    setToast({ type, message, id: Date.now() })
  }, [])

  const clearSelection = useCallback(() => {
    setSelectedFile(null)
    setProgress(0)
    setValidationError(null)
    if (inputRef.current) inputRef.current.value = ''
  }, [])

  const selectFile = useCallback((file) => {
    if (!file) return
    if (!isAcceptedFile(file)) {
      setSelectedFile(null)
      setValidationError('Only CSV, XLSX, and JSON files are supported.')
      showToast('error', 'Only CSV, XLSX, and JSON files are supported.')
      return
    }
    setValidationError(null)
    setSelectedFile(file)
    setProgress(0)
  }, [showToast])

  const onInputChange = (event) => {
    const file = event.target.files?.[0]
    selectFile(file)
  }

  const onDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    if (uploading) return
    const file = event.dataTransfer.files?.[0]
    selectFile(file)
  }

  const onDragOver = (event) => {
    event.preventDefault()
    if (!uploading) setIsDragging(true)
  }

  const onDragLeave = (event) => {
    event.preventDefault()
    setIsDragging(false)
  }

  const handleUpload = async () => {
    if (!selectedFile || uploading) return

    setUploading(true)
    setProgress(0)
    setValidationError(null)
    clearError()

    try {
      const result = await uploadDataset(selectedFile, {
        onUploadProgress: (event) => {
          if (!event.total) {
            setProgress((prev) => (prev < 90 ? prev + 5 : prev))
            return
          }
          const percent = Math.min(100, Math.round((event.loaded / event.total) * 100))
          setProgress(percent)
        },
      })

      setProgress(100)
      showToast(
        'success',
        `Uploaded ${result.original_filename || selectedFile.name} successfully.`,
      )

      window.setTimeout(() => {
        navigate('/overview')
      }, 700)
    } catch (err) {
      setProgress(0)
      showToast('error', err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="page upload-page">
      <header className="page__header">
        <span className="page__eyebrow">Ingestion</span>
        <h2 className="page__heading">Upload dataset</h2>
        <p className="page__description">
          Drop a CSV, Excel (.xlsx), or JSON file to ingest it into DataForge.
        </p>
      </header>

      <section
        className={`upload-dropzone${isDragging ? ' upload-dropzone--active' : ''}${
          uploading ? ' upload-dropzone--disabled' : ''
        }`}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        aria-label="File upload dropzone"
      >
        <div className="upload-dropzone__icon" aria-hidden="true">
          <FiUploadCloud size={36} />
        </div>
        <p className="upload-dropzone__title">Drag & drop your file here</p>
        <p className="upload-dropzone__hint">CSV · XLSX · JSON</p>

        <input
          ref={inputRef}
          id={inputId}
          type="file"
          className="upload-dropzone__input"
          accept={ACCEPT_ATTR}
          disabled={uploading}
          onChange={onInputChange}
        />

        <label htmlFor={inputId} className="upload-browse-btn">
          Browse Files
        </label>
      </section>

      {selectedFile ? (
        <section className="upload-file-card" aria-live="polite">
          <div className="upload-file-card__icon" aria-hidden="true">
            <FiFile size={20} />
          </div>
          <div className="upload-file-card__meta">
            <p className="upload-file-card__name">{selectedFile.name}</p>
            <p className="upload-file-card__size">{formatFileSize(selectedFile.size)}</p>
          </div>
          <button
            type="button"
            className="upload-file-card__clear"
            onClick={clearSelection}
            disabled={uploading}
            aria-label="Remove selected file"
          >
            <FiX size={16} aria-hidden="true" />
          </button>
        </section>
      ) : null}

      {validationError ? (
        <p className="upload-validation" role="alert">
          {validationError}
        </p>
      ) : null}

      {(uploading || progress > 0) && selectedFile ? (
        <section className="upload-progress" aria-label="Upload progress">
          <div className="upload-progress__header">
            <span>{uploading ? 'Uploading…' : 'Upload complete'}</span>
            <span>{progress}%</span>
          </div>
          <div
            className="upload-progress__track"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
          >
            <div
              className="upload-progress__bar"
              style={{ width: `${progress}%` }}
            />
          </div>
        </section>
      ) : null}

      <div className="upload-actions">
        <button
          type="button"
          className="upload-submit-btn"
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
        >
          {uploading ? 'Uploading…' : 'Upload to DataForge'}
        </button>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

export default Upload
