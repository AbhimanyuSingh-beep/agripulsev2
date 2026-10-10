/**
 * VideoLinks.jsx — YouTube prevention / treatment video links
 * Opens YouTube search results for the detected condition, in the
 * currently selected language (English or Hindi).
 */
import { UI, ytLinks } from '../i18n'

export default function VideoLinks({ itemKey, lang }) {
  const t = UI[lang]
  const links = ytLinks(itemKey, lang)
  return (
    <div className="video-section">
      <h3>{t.videosTitle}</h3>
      <p className="video-note">{t.videosNote}</p>
      <div className="video-list">
        {links.map((l) => (
          <a key={l.label} href={l.url} target="_blank" rel="noopener noreferrer" className="video-link">
            <span className="yt-icon">▶</span>
            <span>{l.label}</span>
          </a>
        ))}
      </div>
    </div>
  )
}
