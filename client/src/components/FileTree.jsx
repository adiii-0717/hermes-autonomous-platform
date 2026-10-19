import React, { useState } from 'react';
import { Folder, FolderOpen, FileText, ChevronRight, ChevronDown, Code, Search, Filter } from 'lucide-react';

export default function FileTree({ files, onSelectFile, selectedFile }) {
  const [filter, setFilter] = useState('');
  const [expandedFolders, setExpandedFolders] = useState({});

  // Filter out system noise / zips / logs / internal manifests / temp files
  const isSystemFile = (filename) => {
    if (!filename) return true;
    const lower = filename.toLowerCase();
    return (
      lower.endsWith('.zip') ||
      lower.endsWith('.log') ||
      lower.endsWith('.pyc') ||
      lower === '.project_manifest.json' ||
      lower === '.ds_store' ||
      lower.startsWith('.') ||
      lower === '__pycache__' ||
      lower === '.pytest_cache' ||
      lower === 'node_modules'
    );
  };

  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };

  const workspaceItems = (files || []).filter(item => !isSystemFile(item.name || item.path || ''));

  const filteredFiles = workspaceItems.filter(item => {
    if (!filter) return true;
    const name = item.name || item.path || '';
    return name.toLowerCase().includes(filter.toLowerCase());
  });

  const renderNode = (item, level = 0) => {
    const isDir = item.type === 'directory' || (item.children && item.children.length > 0);
    const path = item.path || item.name;
    const isExpanded = !!expandedFolders[path];
    const isSelected = selectedFile && (selectedFile.path === path || selectedFile === path);

    const paddingVal = (level * 12) + 'px';

    return (
      <div key={path} style={{ paddingLeft: paddingVal }}>
        <div
          className={'file-tree-item ' + (isSelected ? 'selected' : '')}
          onClick={() => {
            if (isDir) {
              toggleFolder(path);
            } else {
              onSelectFile(item);
            }
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 8px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.85rem',
            color: isSelected ? 'var(--accent-primary, #06b6d4)' : 'var(--text-main, #e2e8f0)',
            background: isSelected ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
            userSelect: 'none'
          }}
        >
          {isDir ? (
            <>
              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              {isExpanded ? <FolderOpen size={16} color="#38bdf8" /> : <Folder size={16} color="#38bdf8" />}
            </>
          ) : (
            <>
              <FileText size={15} color="#94a3b8" />
            </>
          )}
          <span className="file-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {item.name || path.split('/').pop()}
          </span>
        </div>

        {isDir && isExpanded && item.children && (
          <div className="folder-children">
            {item.children.filter(c => !isSystemFile(c.name || c.path || '')).map(c => renderNode(c, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="file-tree-container" style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '8px', padding: '8px' }}>
      <div className="file-tree-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8' }}>
          Workspace Files
        </span>
      </div>

      <div className="file-tree-search" style={{ position: 'relative' }}>
        <Search size={14} style={{ position: 'absolute', left: '8px', top: '8px', color: '#64748b' }} />
        <input
          type="text"
          placeholder="Search files..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{
            width: '100%',
            padding: '6px 8px 6px 28px',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '4px',
            color: '#fff',
            fontSize: '0.8rem'
          }}
        />
      </div>

      <div className="file-tree-list" style={{ flex: 1, overflowY: 'auto' }}>
        {filteredFiles.length === 0 ? (
          <div style={{ fontSize: '0.8rem', color: '#64748b', padding: '12px 8px', textAlign: 'center' }}>
            No files found
          </div>
        ) : (
          filteredFiles.map(item => renderNode(item, 0))
        )}
      </div>
    </div>
  );
}
