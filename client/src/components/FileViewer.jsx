import React, { useState } from 'react';
import { Save, Code, Copy, Check } from 'lucide-react';

export default function FileViewer({ path, content, onChange, onSave }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!content) return;
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!path) {
    return (
      <div className="editor-view" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', textAlign: 'center', padding: '2rem' }}>
        <div>
          <Code size={48} style={{ opacity: 0.3, marginBottom: '1rem', color: 'var(--accent-primary)' }} />
          <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-muted)' }}>No File Selected</div>
          <div style={{ fontSize: '0.82rem', marginTop: '0.4rem' }}>Select a file from the project explorer to view or edit code.</div>
        </div>
      </div>
    );
  }

  const lineCount = content ? content.split('\n').length : 0;

  return (
    <div className="editor-view">
      <div className="editor-toolbar">
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--accent-primary)', fontWeight: 600 }}>
          {path}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{lineCount} lines</span>

          <button
            onClick={handleCopy}
            style={{
              background: 'var(--bg-hover)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-main)',
              borderRadius: '6px',
              padding: '0.3rem 0.65rem',
              fontSize: '0.78rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            {copied ? <Check size={13} style={{ color: 'var(--success)' }} /> : <Copy size={13} />}
            {copied ? 'Copied' : 'Copy'}
          </button>

          <button
            onClick={onSave}
            style={{
              background: 'var(--accent-gradient)',
              border: 'none',
              borderRadius: '6px',
              padding: '0.35rem 0.85rem',
              color: '#ffffff',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              boxShadow: '0 2px 8px rgba(99, 102, 241, 0.3)'
            }}
          >
            <Save size={13} /> Save File
          </button>
        </div>
      </div>
      
      <textarea
        className="editor-textarea"
        value={content}
        onChange={(e) => onChange(e.target.value)}
        placeholder="File content is empty..."
      />
    </div>
  );
}
