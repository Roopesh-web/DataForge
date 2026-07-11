import { useCallback, useId, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiFile, FiUploadCloud, FiX } from 'react-icons/fi'
import { useToast } from '../hooks/useToast'
import { useDataset } from '../hooks/useDataset'

const ACCEPTED_EXTENSIONS = ['.csv', '.xlsx', '.json']
const ACCEPT_ATTR =
  '.csv,.xlsx,.json,text/csv,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
const MAX_UPLOAD_BYTES = 100 * 1024 * 1024

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

function validateFile(file) {
  if (!file) return 'Choose a file to upload.'
  if (!file.name?.trim()) return 'The selected file is missing a name.'
  if (!ACCEPTED_EXTENSIONS.includes(getExtension(file.name))) {
    return 'Only CSV, XLSX, and JSON files are supported.'
  }
  if (!file.size) return 'The selected file is empty.'
  if (file.size > MAX_UPLOAD_BYTES) {
    return `File exceeds the ${formatFileSize(MAX_UPLOAD_BYTES)} upload limit.`
  }
  return null
}

function Upload() {
  const inputId = useId()
  const inputRef = useRef(null)
  const inFlightRef = useRef(false)
  const navigate = useNavigate()
  const toast = useToast()
  const { uploadDataset, clearError, loading } = useDataset()

  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [validationError, setValidationError] = useState(null)

  const busy = uploading || loading

  const clearSelection = useCallback(() => {
    setSelectedFile(null)
    setProgress(0)
    setValidationError(null)
    if (inputRef.current) inputRef.current.value = ''
  }, [])

  const selectFile = useCallback(
    (file) => {
      if (!file) return
      const problem = validateFile(file)
      if (problem) {
        setSelectedFile(null)
        setValidationError(problem)
        toast.error(problem)
        if (inputRef.current) inputRef.current.value = ''
        return
      }
      setValidationError(null)
      setSelectedFile(file)
      setProgress(0)
    },
    [toast],
  )

  const onInputChange = (event) => {
    selectFile(event.target.files?.[0])
  }

  const onDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    if (busy) return
    selectFile(event.dataTransfer.files?.[0])
  }

  const onDragOver = (event) => {
    event.preventDefault()
    if (!busy) setIsDragging(true)
  }

  const onDragLeave = (event) => {
    event.preventDefault()
    setIsDragging(false)
  }

  const onDropzoneKeyDown = (event) => {
    if (busy) return
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      inputRef.current?.click()
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || busy || inFlightRef.current) return

    const problem = validateFile(selectedFile)
    if (problem) {
      setValidationError(problem)
      toast.error(problem)
      return
    }

    inFlightRef.current = true
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
      toast.success(
        `Uploaded ${result.original_filename || selectedFile.name} successfully.`,
      )

      // Context already updated storedFilename/dataset before uploadDataset resolved.
      navigate('/overview')
    } catch (err) {
      if (err?.error === 'REQUEST_CANCELLED') return
      setProgress(0)
      toast.error(err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
      inFlightRef.current = false
    }
  }

  return (
    <div className="page upload-page">
      <header className="page__header upload-page__header">
        <span className="page__eyebrow">Ingestion</span>
        <h2 className="page__heading">Upload dataset</h2>
        <p className="page__description">
          Drop a CSV, Excel (.xlsx), or JSON file to ingest it into DataForge.
        </p>
      </header>

      <div className="upload-shell">
        <div className="upload-card">
          <section
            className={`upload-dropzone${isDragging ? ' upload-dropzone--active' : ''}${
              busy ? ' upload-dropzone--disabled' : ''
            }`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onKeyDown={onDropzoneKeyDown}
            tabIndex={busy ? -1 : 0}
            role="button"
            aria-label="File upload dropzone. Press Enter to browse files."
            aria-disabled={busy}
          >
            <div className="upload-dropzone__icon" aria-hidden="true">
              <FiUploadCloud size={40} />
            </div>
            <p className="upload-dropzone__title">Drag & drop your file here</p>
            <p className="upload-dropzone__hint">CSV · XLSX · JSON · max 100 MB</p>

            <input
              ref={inputRef}
              id={inputId}
              type="file"
              className="upload-dropzone__input"
              accept={ACCEPT_ATTR}
              disabled={busy}
              onChange={onInputChange}
            />

            <label
              htmlFor={inputId}
              className={`upload-browse-btn${busy ? ' is-disabled' : ''}`}
              aria-disabled={busy}
            >
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
                disabled={busy}
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

          {(busy || progress > 0) && selectedFile ? (
            <section className="upload-progress" aria-label="Upload progress">
              <div className="upload-progress__header">
                <span>{busy ? 'Uploading…' : 'Upload complete'}</span>
                <span>{progress}%</span>
              </div>
              <div
                className="upload-progress__track"
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={progress}
              >
                <div className="upload-progress__bar" style={{ width: `${progress}%` }} />
              </div>
            </section>
          ) : null}

          <div className="upload-actions">
            <button
              type="button"
              className="upload-submit-btn"
              onClick={handleUpload}
              disabled={!selectedFile || busy}
              aria-busy={busy}
            >
              {busy ? 'Uploading…' : 'Upload to DataForge'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Upload
