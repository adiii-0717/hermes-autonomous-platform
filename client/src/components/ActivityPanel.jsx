import React from 'react';
import { Activity, Cpu, CheckCircle, AlertCircle } from 'lucide-react';

export default function ActivityPanel({ manifest, health }) {
  return (
    <div style={{ padding: '1.25rem', color: 'var(--text-main)', height: '100%', overflowY: 'auto' }}>
      {/* Project Manifest Overview */}
      <div style={{ background: 'var(--bg-card)', padding: '1.1rem 1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)', marginBottom: '1.25rem', boxShadow: 'var(--card-shadow)' }}>
        <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.92rem', color: 'var(--accent-primary)', fontWeight: 800, marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Cpu size={16} /> Tech Stack & Manifest
        </h4>
        
        {manifest ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem', fontSize: '0.82rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Languages:</span>
              <div style={{ fontWeight: 700, color: 'var(--text-main)', marginTop: '0.15rem' }}>{manifest.languages?.join(', ') || 'N/A'}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Frameworks:</span>
              <div style={{ fontWeight: 700, color: 'var(--text-main)', marginTop: '0.15rem' }}>{manifest.frameworks?.join(', ') || 'N/A'}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Package Managers:</span>
              <div style={{ fontWeight: 700, color: 'var(--text-main)', marginTop: '0.15rem' }}>{manifest.package_managers?.join(', ') || 'N/A'}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Testing Suite:</span>
              <div style={{ fontWeight: 700, color: 'var(--text-main)', marginTop: '0.15rem' }}>{manifest.test_frameworks?.join(', ') || 'N/A'}</div>
            </div>
          </div>
        ) : (
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Loading project manifest...</div>
        )}
      </div>

      {/* Project Health Status */}
      <div style={{ background: 'var(--bg-card)', padding: '1.1rem 1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)', boxShadow: 'var(--card-shadow)' }}>
        <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.92rem', color: 'var(--accent-cyan)', fontWeight: 800, marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Activity size={16} /> Workspace Health Status
        </h4>

        {health ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.84rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-muted)' }}>Build Suite</span>
              {health.build_healthy ? (
                <span style={{ color: 'var(--success)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}><CheckCircle size={14} /> Healthy</span>
              ) : (
                <span style={{ color: 'var(--danger)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}><AlertCircle size={14} /> Failing</span>
              )}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-muted)' }}>Unit Tests</span>
              {health.tests_healthy ? (
                <span style={{ color: 'var(--success)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}><CheckCircle size={14} /> Passing</span>
              ) : (
                <span style={{ color: 'var(--danger)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}><AlertCircle size={14} /> Failing</span>
              )}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-muted)' }}>Code Linter</span>
              {health.lint_healthy ? (
                <span style={{ color: 'var(--success)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}><CheckCircle size={14} /> Clean</span>
              ) : (
                <span style={{ color: 'var(--warning)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}><AlertCircle size={14} /> Warnings</span>
              )}
            </div>
          </div>
        ) : (
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Evaluating workspace health...</div>
        )}
      </div>
    </div>
  );
}
