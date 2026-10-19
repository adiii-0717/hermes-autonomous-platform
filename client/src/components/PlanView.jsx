import React from 'react';
import { 
  CheckCircle2, Circle, Clock, AlertTriangle, CheckSquare, 
  Loader2, ArrowRight, Layers, Cpu
} from 'lucide-react';

export default function PlanView({ plan, onGoToChat }) {
  if (!plan || !plan.tasks || plan.tasks.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%', 
        minHeight: '400px',
        padding: '3rem 1.5rem', 
        textAlign: 'center' 
      }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '16px',
          background: 'rgba(217, 164, 32, 0.08)',
          border: '1px solid rgba(217, 164, 32, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.25rem',
          color: 'var(--accent-gold)'
        }}>
          <CheckSquare size={32} />
        </div>
        <h3 style={{ 
          fontFamily: 'var(--font-heading)', 
          fontSize: '1.35rem', 
          fontWeight: 800, 
          color: 'var(--text-heading)',
          marginBottom: '0.5rem'
        }}>
          Execution Plan Mission Control
        </h3>
        <p style={{ 
          fontSize: '0.88rem', 
          color: 'var(--text-muted)', 
          maxWidth: '460px', 
          lineHeight: 1.55,
          marginBottom: '1.75rem' 
        }}>
          When NEXARCH AI agents begin planning and engineering your software project, real-time architecture phases, execution tasks, and progress milestones stream directly here.
        </p>
        {onGoToChat && (
          <button 
            onClick={onGoToChat}
            className="btn-new-project"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.65rem 1.25rem', cursor: 'pointer' }}
          >
            <span>Start a Project Prompt</span>
            <ArrowRight size={15} />
          </button>
        )}
      </div>
    );
  }

  const completedCount = plan.tasks.filter(t => t.status === 'COMPLETED').length;
  const inProgressTask = plan.tasks.find(t => t.status === 'IN_PROGRESS');
  const rawProgress = plan.overall_progress ?? (plan.tasks.length > 0 
    ? Math.round((completedCount / plan.tasks.length) * 100) 
    : 0);
  const progress = Math.min(100, Math.max(0, rawProgress));
  const isFinished = completedCount === plan.tasks.length && plan.tasks.length > 0;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span style={{ 
            color: '#10B981', 
            background: 'rgba(16, 185, 129, 0.1)', 
            border: '1px solid rgba(16, 185, 129, 0.25)', 
            padding: '3px 8px', 
            borderRadius: '12px', 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '0.3rem', 
            fontSize: '0.72rem', 
            fontWeight: 700 
          }}>
            <CheckCircle2 size={13} /> Completed
          </span>
        );
      case 'IN_PROGRESS':
        return (
          <span style={{ 
            color: 'var(--accent-gold)', 
            background: 'rgba(217, 164, 32, 0.12)', 
            border: '1px solid rgba(217, 164, 32, 0.3)', 
            padding: '3px 8px', 
            borderRadius: '12px', 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '0.35rem', 
            fontSize: '0.72rem', 
            fontWeight: 800 
          }}>
            <Loader2 size={13} className="animate-spin" /> Currently Executing
          </span>
        );
      case 'FAILED':
        return (
          <span style={{ 
            color: '#EF4444', 
            background: 'rgba(239, 68, 68, 0.1)', 
            border: '1px solid rgba(239, 68, 68, 0.25)', 
            padding: '3px 8px', 
            borderRadius: '12px', 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '0.3rem', 
            fontSize: '0.72rem', 
            fontWeight: 700 
          }}>
            <AlertTriangle size={13} /> Failed
          </span>
        );
      default:
        return (
          <span style={{ 
            color: 'var(--text-dim)', 
            background: 'var(--bg-chip)', 
            border: '1px solid var(--border-subtle)', 
            padding: '3px 8px', 
            borderRadius: '12px', 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '0.3rem', 
            fontSize: '0.72rem',
            fontWeight: 600
          }}>
            <Circle size={12} /> Queued
          </span>
        );
    }
  };

  return (
    <div style={{ padding: '0.5rem', color: 'var(--text-main)', height: '100%', overflowY: 'auto' }}>
      
      {/* 1. Header Mission Control Overview Card */}
      <div style={{ 
        marginBottom: '1.5rem', 
        background: 'var(--bg-card)', 
        padding: '1.4rem 1.5rem', 
        borderRadius: '14px', 
        border: '1px solid var(--border-color)', 
        boxShadow: 'var(--shadow-card)' 
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
          <span style={{ 
            fontSize: '0.68rem', 
            fontWeight: 800, 
            letterSpacing: '0.08em', 
            textTransform: 'uppercase', 
            color: isFinished ? '#10B981' : 'var(--accent-gold)', 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '0.4rem' 
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: isFinished ? '#10B981' : 'var(--accent-gold)',
              boxShadow: isFinished ? '0 0 8px rgba(16, 185, 129, 0.6)' : '0 0 8px rgba(217, 164, 32, 0.8)'
            }} />
            {isFinished ? 'PLAN EXECUTION COMPLETE' : 'MULTI-AGENT PIPELINE ACTIVE'}
          </span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            {completedCount} of {plan.tasks.length} Phases Done
          </span>
        </div>

        <h3 style={{ 
          fontFamily: 'var(--font-heading)', 
          fontSize: '1.25rem', 
          fontWeight: 800, 
          color: 'var(--text-heading)', 
          marginBottom: '0.4rem', 
          letterSpacing: '-0.01em' 
        }}>
          {plan.title}
        </h3>

        {plan.requirement && (
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.2rem', lineHeight: 1.5 }}>
            {plan.requirement}
          </p>
        )}

        {/* Progress Bar & Percentage */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.45rem' }}>
          <span>Overall Engineering Progress</span>
          <span style={{ color: isFinished ? '#10B981' : 'var(--accent-gold)', fontSize: '0.9rem', fontWeight: 800 }}>
            {progress}%
          </span>
        </div>
        <div style={{ width: '100%', height: '8px', background: 'var(--bg-chip)', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ 
            width: `${Math.max(progress, 4)}%`, 
            height: '100%', 
            background: isFinished ? '#10B981' : 'var(--accent-gold-gradient, #C28E0E)', 
            borderRadius: '4px',
            transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)' 
          }} />
        </div>

        {/* Current Active Phase Highlight */}
        {inProgressTask && (
          <div style={{ 
            marginTop: '1rem', 
            padding: '0.65rem 0.85rem', 
            background: 'rgba(217, 164, 32, 0.06)', 
            border: '1px solid rgba(217, 164, 32, 0.2)', 
            borderRadius: '8px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.55rem', 
            fontSize: '0.8rem', 
            color: 'var(--text-heading)' 
          }}>
            <Cpu size={15} style={{ color: 'var(--accent-gold)', flexShrink: 0 }} />
            <span>
              <strong>Executing Now:</strong> {inProgressTask.title} — {inProgressTask.description}
            </span>
          </div>
        )}
      </div>

      {/* 2. Structured Task Execution Timeline */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', padding: '0 0.2rem' }}>
        <h4 style={{ 
          fontSize: '0.74rem', 
          fontWeight: 800, 
          color: 'var(--text-dim)', 
          textTransform: 'uppercase', 
          letterSpacing: '0.08em', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.4rem' 
        }}>
          <Layers size={14} /> Execution Phases & Milestones
        </h4>
        <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
          Sequential Pipeline
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
        {plan.tasks.map((task, idx) => {
          const isActive = task.status === 'IN_PROGRESS';
          const isDone = task.status === 'COMPLETED';
          const isFail = task.status === 'FAILED';

          return (
            <div 
              key={task.id || idx} 
              style={{ 
                background: isActive ? 'var(--bg-card)' : 'var(--bg-panel)', 
                border: isActive 
                  ? '1.5px solid var(--accent-gold)' 
                  : isDone 
                    ? '1px solid rgba(16, 185, 129, 0.25)' 
                    : '1px solid var(--border-color)', 
                borderRadius: '12px', 
                padding: '1.05rem 1.25rem', 
                boxShadow: isActive ? '0 4px 16px rgba(217, 164, 32, 0.12)' : 'var(--shadow-sm)',
                transition: 'all 0.2s ease',
                position: 'relative'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.8rem' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', flex: 1 }}>
                  <div style={{ 
                    width: '26px', 
                    height: '26px', 
                    borderRadius: '8px', 
                    background: isDone ? 'rgba(16, 185, 129, 0.15)' : isActive ? 'rgba(217, 164, 32, 0.15)' : 'var(--bg-chip)', 
                    color: isDone ? '#10B981' : isActive ? 'var(--accent-gold)' : 'var(--text-dim)',
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    fontSize: '0.76rem', 
                    fontWeight: 800,
                    flexShrink: 0,
                    marginTop: '2px'
                  }}>
                    {isDone ? <CheckCircle2 size={16} /> : isActive ? <Loader2 size={15} className="animate-spin" /> : idx + 1}
                  </div>
                  <div>
                    <div style={{ 
                      fontWeight: 800, 
                      fontSize: '0.92rem', 
                      color: isActive ? 'var(--text-heading)' : 'var(--text-main)',
                      marginBottom: '0.2rem'
                    }}>
                      {task.title}
                    </div>
                    {task.description && (
                      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
                        {task.description}
                      </p>
                    )}
                  </div>
                </div>

                <div style={{ flexShrink: 0 }}>
                  {getStatusBadge(task.status)}
                </div>
              </div>

              {task.error_message && (
                <div style={{ 
                  background: 'rgba(239, 68, 68, 0.1)', 
                  color: '#ef4444', 
                  border: '1px solid rgba(239, 68, 68, 0.25)', 
                  padding: '0.5rem 0.75rem', 
                  borderRadius: '6px', 
                  fontSize: '0.78rem', 
                  marginTop: '0.75rem', 
                  fontFamily: 'var(--font-mono)' 
                }}>
                  {task.error_message}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
