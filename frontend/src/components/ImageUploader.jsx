/**
 * ImageUploader.jsx
 * Handles drag-and-drop, file picker, and camera capture.
 * Shows a preview of the selected image before analysis.
 */
import { useState, useRef, useCallback } from 'react'
import { UI } from '../i18n'

const CROP_ICONS = { Tomato: '🍅', Corn: '🌽' }

export default function ImageUploader({ onImageSelect, selectedFile, onAnalyze, isLoading, lang = 'en' }) {
  const t = UI[lang]
  const [isDragOver, setIsDragOver] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(null)
  const fileInputRef   = useRef(null)
  const cameraInputRef = useRef(null)

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    onImageSelect(file)
  }, [onImageSelect])

  const handleFileInput = (e) => handleFile(e.target.files?.[0])

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  const handleDragOver = (e) => { e.preventDefault(); setIsDragOver(true) }
  const handleDragLeave = () => setIsDragOver(false)

  const clearImage = () => {
    setPreviewUrl(null)
    onImageSelect(null)
    if (fileInputRef.current)   fileInputRef.current.value   = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }

  return (
    <div className="uploader">
      <h2>{t.uploadTitle}</h2>

      {!previewUrl ? (
        <>
          {/* Drop zone */}
          <div
            className={`drop-zone ${isDragOver ? 'drag-active' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileInput}
              id="file-upload"
            />
            <span className="drop-zone-icon">🍃</span>
            <h3>{t.dragDrop}</h3>
            <p>
              {t.or} <span className="browse-link">{t.browseFiles}</span>
            </p>
            <p style={{ marginTop: '0.4rem', fontSize: '0.78rem' }}>
              {t.formats}
            </p>
          </div>

          {/* Camera capture (works on mobile) */}
          <div>
            <button className="camera-btn" type="button">
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFileInput}
                aria-label={t.camera}
              />
              {t.camera}
            </button>
          </div>

          {/* Crop tags */}
          <div style={{ marginTop: '1.5rem', opacity: 0.85, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {t.supports}: {Object.entries(CROP_ICONS).map(([c, ic]) => (
              <span key={c} style={{ margin: '0 0.3rem' }}>{ic} {t.crops[c]}</span>
            ))}
          </div>
        </>
      ) : (
        /* Image preview */
        <div>
          <div className="preview-container">
            <img
              src={previewUrl}
              alt="Selected crop leaf"
              className="preview-image"
            />
            <button
              className="preview-clear-btn"
              onClick={clearImage}
              title={t.removeImage}
              aria-label={t.removeImage}
            >
              ×
            </button>
          </div>

          <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            📎 {selectedFile?.name} ({(selectedFile?.size / 1024).toFixed(0)} KB)
          </div>

          <div>
            <button
              className={`analyze-btn ${isLoading ? 'loading' : ''}`}
              onClick={onAnalyze}
              disabled={!selectedFile || isLoading}
              id="analyze-btn"
            >
              {isLoading ? (
                <>
                  <span className="spinner" />
                  {t.analyzing}
                </>
              ) : (
                <>
                  {t.analyze}
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
