import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Bot, User, CheckCircle, Download, Terminal, Cpu, Clock, Sparkles, 
  Folder, Play, Code, Eye, Camera, ShieldCheck, Box, 
  Paperclip, ChevronDown, Check, ArrowRight, ExternalLink
} from 'lucide-react';

export default function ChatPanel({ 
  messages, 
  onSendMessage, 
  isProcessing, 
  currentRunId, 
  heartbeat, 
  onRefreshWorkspace,
  onOpenPreview,
  activeProvider
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing, heartbeat]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;
    onSendMessage(input);
    setInput('');
  };

  const renderFormattedText = (text) => {
    if (!text) return null;
    const downloadRegex = /\[([^\]]+)\]\(([^\)]+)\)|(\/(?:api\/projects\/[^\s\)]+\/download|api\/workspace\/download))/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = downloadRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const title = match[1] || 'Download Complete Project (.ZIP)';
      const url = match[2] || match[3];

      parts.push(
        <div key={match.index} style={{ margin: '0.85rem 0', background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '0.85rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <strong style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-heading)' }}>📦 {title}</strong>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{url}</span>
          </div>
          <a href={url} download className="download-btn-primary">
            <Download size={14} /> Download ZIP
          </a>
        </div>
      );
      lastIndex = downloadRegex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return <div>{parts.map((p, idx) => typeof p === 'string' ? <span key={idx}>{p}</span> : p)}</div>;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.25rem' }}>
      
      {/* 1. Editorial Welcome Hero Banner */}
      <div className="hero-welcome-card">
        <div className="hero-content">
          <div className="hero-subtitle-tracking">WELCOME TO NEXARCH</div>
          <h1 className="hero-title-editorial">
            Build Ideas <br />
            Into <span className="accent-italic">Reality</span>
          </h1>
          <p className="hero-description">
            Intelligence, Architected. Your multi-agent AI software engineering platform where specialized agents collaborate to plan, architect, develop, test, and review software projects.
          </p>
        </div>

        {/* Decorative 3D Glassmorphic Crystal Cube */}
        <div className="hero-3d-graphic-container">
          <div className="crystal-cube-visual">
            <div className="cube-inner-core"></div>
            <div className="step-tag-badge step-tag-1">DESIGN</div>
            <div className="step-tag-badge step-tag-2">DEVELOP</div>
            <div className="step-tag-badge step-tag-3">TEST</div>
            <div className="step-tag-badge step-tag-4">DEPLOY</div>
          </div>
        </div>
      </div>

      {/* 3. Conversation Messages Stream */}
      <div className="chat-conversation-stream" style={{ flex: 1, overflowY: 'auto' }}>
        {messages.map((msg, index) => {
          if (msg.sender === 'user') {
            return (
              <div key={index} className="chat-message-bubble" style={{ background: 'var(--bg-card)' }}>
                <div className="msg-header">
                  <div className="msg-author">
                    <User size={16} style={{ color: 'var(--text-muted)' }} />
                    <span>You</span>
                  </div>
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', fontWeight: 500 }}>
                  {msg.content}
                </div>
              </div>
            );
          }

          return (
            <div key={index} className="chat-message-bubble">
              <div className="msg-header">
                <div className="msg-author">
                  <div className="author-badge-agent">
                    <Sparkles size={13} style={{ color: 'var(--accent-gold)' }} />
                  </div>
                  <span>NEXARCH Agent</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  {isProcessing && index === messages.length - 1 && (
                    <span className="msg-status-running">• Processing...</span>
                  )}
                </div>
              </div>

              {msg.thinking && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', background: 'var(--bg-panel)', padding: '0.6rem 0.85rem', borderRadius: '8px', borderLeft: '3px solid var(--accent-gold)' }}>
                  💭 {msg.thinking}
                </div>
              )}

                            {msg.type === 'project_selection_required' && msg.projects && (
                <div style={{ marginTop: '0.85rem', background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-heading)', marginBottom: '0.6rem' }}>
                    Matching Projects in Workspace:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {msg.projects.map((proj, pIdx) => (
                      <button
                        key={pIdx}
                        type="button"
                        className="download-btn-primary"
                        style={{ width: 'fit-content', padding: '6px 12px', fontSize: '0.8rem' }}
                        onClick={() => {
                          if (window.__hermes_ws && window.__hermes_ws.readyState === WebSocket.OPEN) {
                            window.__hermes_ws.send(JSON.stringify({
                              type: 'project_selected',
                              project_name: proj,
                              content: msg.prompt
                            }));
                          } else {
                            onSendMessage(`Continue project ${proj}: ${msg.prompt}`);
                          }
                        }}
                      >
                        <Folder size={13} /> {proj}
                      </button>
                    ))}
                    <button
                      type="button"
                      className="download-btn-primary"
                      style={{ width: 'fit-content', padding: '6px 12px', fontSize: '0.8rem', background: 'var(--bg-card)', color: 'var(--text-heading)', border: '1px solid var(--border-color)' }}
                      onClick={() => {
                        if (window.__hermes_ws && window.__hermes_ws.readyState === WebSocket.OPEN) {
                          window.__hermes_ws.send(JSON.stringify({
                            type: 'project_selected',
                            project_name: '_new_project_',
                            content: msg.prompt
                          }));
                        } else {
                          onSendMessage(`Create new project: ${msg.prompt}`);
                        }
                      }}
                    >
                      + Create New Project
                    </button>
                  </div>
                </div>
              )}

              {msg.type === 'error' && (
                <div style={{ margin: '0.5rem 0', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '12px', padding: '0.85rem 1rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
                    ⚠️ Service Notice
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                    {msg.content}
                  </div>
                </div>
              )}

              {msg.content && msg.type !== 'error' && (
                <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                  {renderFormattedText(msg.content)}
                </div>
              )}

              {msg.type === 'build_completion' && (
                <div style={{ marginTop: '0.85rem', background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1rem' }}>
                  <div style={{ fontWeight: 800, fontSize: '0.92rem', color: msg.success ? 'var(--success)' : 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    {msg.success ? '✓ BUILD & COMPILATION SUCCESSFUL' : '❌ BUILD FAILED / COMPLETED WITH ISSUES'}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                    Project: <strong>{msg.project_name}</strong>
                  </div>
                  {msg.preview_url && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginTop: '0.75rem' }}>
                      <button 
                        type="button"
                        className="download-btn-primary" 
                        style={{ width: 'fit-content' }}
                        onClick={() => onOpenPreview(msg.project_name)}
                      >
                        <Eye size={14} /> View Live Preview
                      </button>
                      <a 
                        href={`/preview/${msg.project_name}/`}
                        target="_blank"
                        rel="noreferrer"
                        className="download-btn-primary"
                        style={{ width: 'fit-content', background: 'var(--bg-card)', color: 'var(--text-heading)', border: '1px solid var(--border-color)' }}
                      >
                        Open New Tab <ExternalLink size={13} />
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* 4. Bottom Prompt Composer */}
      <form onSubmit={handleSubmit} className="prompt-composer-container">
        <div className="composer-input-wrapper">
          <textarea
            className="composer-textarea"
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask NEXARCH to build, modify, debug or enhance your project..."
          />

          <div className="composer-actions">
            {isProcessing ? (
              <button
                type="button"
                className="btn-send-circle"
                style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.4)' }}
                onClick={() => {
                  if (window.__hermes_ws && window.__hermes_ws.readyState === WebSocket.OPEN) {
                    window.__hermes_ws.send(JSON.stringify({ type: 'cancel' }));
                  }
                }}
                title="Stop generation"
              >
                <span style={{ fontSize: '11px', fontWeight: 800 }}>⏹</span>
              </button>
            ) : (
              <button type="submit" className="btn-send-circle" disabled={!input.trim()} title="Send prompt">
                <Send size={15} />
              </button>
            )}
          </div>
        </div>
      </form>

    </div>
  );
}
