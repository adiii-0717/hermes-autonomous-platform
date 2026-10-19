import React from 'react';
import { ShieldAlert, Check, X } from 'lucide-react';

export default function ApprovalModal({ request, onResolve }) {
  if (!request) return null;

  return (
    <div className="modal-overlay">
      <div className="approval-modal">
        <div className="approval-title">
          <ShieldAlert size={22} /> Permission Approval Required
        </div>
        <p style={{ fontSize: '0.88rem', color: '#d1d5db', marginBottom: '1rem' }}>
          NEXARCH Agent requests permission to execute a high-risk operation on the workspace sandbox.
        </p>

        <div style={{ background: '#0d0f17', borderRadius: '6px', padding: '0.85rem', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
          <div style={{ color: '#f59e0b', fontWeight: 600, marginBottom: '0.4rem' }}>
            Action Type: {request.action_type}
          </div>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#e5e7eb' }}>
            {JSON.stringify(request.details, null, 2)}
          </pre>
        </div>

        <div className="approval-actions">
          <button className="btn-reject" onClick={() => onResolve(request.request_id, false)}>
            <X size={16} inline /> Reject
          </button>
          <button className="btn-approve" onClick={() => onResolve(request.request_id, true)}>
            <Check size={16} inline /> Approve & Execute
          </button>
        </div>
      </div>
    </div>
  );
}
