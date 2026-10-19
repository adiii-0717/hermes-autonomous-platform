import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, RefreshCw, Sun, Moon, Code, CheckSquare, Activity, 
  Download, Eye, Terminal, Search, Bell, MoreVertical, Plus, Box, Layers, 
  HardDrive, Zap, ArrowRight, ExternalLink, Play, AlertTriangle, Loader2,
  PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen, Trash2
} from 'lucide-react';
import FileTree from './components/FileTree';
import FileViewer from './components/FileViewer';
import PlanView from './components/PlanView';
import ActivityPanel from './components/ActivityPanel';
import ApprovalModal from './components/ApprovalModal';
import ChatPanel from './components/ChatPanel';
import NexarchLogo from './components/NexarchLogo';

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('hermes_theme') || 'light');
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'editor', 'plan', 'activity', 'preview', 'downloads'
  
  // Resizable & Collapsible Panel States (ChatGPT-inspired layout)
  const [leftWidth, setLeftWidth] = useState(() => {
    const saved = parseInt(localStorage.getItem('hermes_left_width') || '250', 10);
    return Number.isFinite(saved) && saved >= 180 && saved <= 450 ? saved : 250;
  });
  const [rightWidth, setRightWidth] = useState(() => {
    const saved = parseInt(localStorage.getItem('hermes_right_width') || '450', 10);
    return Number.isFinite(saved) && saved >= 280 ? saved : 450;
  });
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(() => localStorage.getItem('hermes_left_collapsed') === 'true');
  const [isRightCollapsed, setIsRightCollapsed] = useState(() => localStorage.getItem('hermes_right_collapsed') === 'true');
  const [isDraggingLeft, setIsDraggingLeft] = useState(false);
  const [isDraggingRight, setIsDraggingRight] = useState(false);
  const layoutRef = useRef(null);

  const [files, setFiles] = useState([]);
  const [selectedFilePath, setSelectedFilePath] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [activePlan, setActivePlan] = useState(null);
  const [manifest, setManifest] = useState(null);
  const [health, setHealth] = useState(null);
  const [projectsList, setProjectsList] = useState([]);
  const [previewProject, setPreviewProject] = useState(null);
  const [previewStatus, setPreviewStatus] = useState('idle'); // 'idle', 'building', 'ready', 'failed'
  
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      content: "Welcome to NEXARCH Dev Studio. Ask NEXARCH to build a software project, run tests, or inspect your workspace.",
      isStreaming: false
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentRunId, setCurrentRunId] = useState(null);
  const [heartbeat, setHeartbeat] = useState({ status: 'idle', elapsed_seconds: 0, latest_tool: null });
  const [terminalLogs, setTerminalLogs] = useState([
    "NEXARCH Workspace Session Initialized.",
    "System ready for engineering operations."
  ]);
  const [approvalRequest, setApprovalRequest] = useState(null);
  const [activeProvider, setActiveProvider] = useState('Gemini (Key 1)');
  const [projectToDelete, setProjectToDelete] = useState(null);
  const [isDeletingProject, setIsDeletingProject] = useState(false);

  useEffect(() => {
    fetch('/api/providers/status')
      .then((r) => r.json())
      .then((data) => {
        if (data && data.providers) {
          const healthy = data.providers.find((p) => p.status === 'HEALTHY' && p.is_configured);
          if (healthy) setActiveProvider(healthy.display_name);
        }
      })
      .catch(() => {});
  }, []);
  const wsRef = useRef(null);
  const processedEventsRef = useRef(new Set());

  // Sync data-theme attribute on root element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('hermes_theme', theme);
  }, [theme]);

  // Persist resizable widths and collapsed states
  useEffect(() => {
    localStorage.setItem('hermes_left_width', leftWidth.toString());
  }, [leftWidth]);

  useEffect(() => {
    localStorage.setItem('hermes_right_width', rightWidth.toString());
  }, [rightWidth]);

  useEffect(() => {
    localStorage.setItem('hermes_left_collapsed', isLeftCollapsed ? 'true' : 'false');
  }, [isLeftCollapsed]);

  useEffect(() => {
    localStorage.setItem('hermes_right_collapsed', isRightCollapsed ? 'true' : 'false');
  }, [isRightCollapsed]);

  // Keyboard shortcuts: Cmd/Ctrl+B for left sidebar, Cmd/Ctrl+\ for right preview
  useEffect(() => {
    const handleKeyDown = (e) => {
      const isMod = e.metaKey || e.ctrlKey;
      if (isMod && e.key.toLowerCase() === 'b') {
        if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
        e.preventDefault();
        setIsLeftCollapsed(prev => !prev);
      } else if (isMod && e.key === '\\') {
        if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
        e.preventDefault();
        setIsRightCollapsed(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Robust, bidirectional mouse/pointer drag handlers with frame batching & container clamping
  useEffect(() => {
    if (!isDraggingLeft && !isDraggingRight) return;

    document.body.classList.add('resizing-active');

    let animId = null;

    const handlePointerMove = (e) => {
      if (animId) return;

      animId = requestAnimationFrame(() => {
        animId = null;
        if (!layoutRef.current) return;
        const rect = layoutRef.current.getBoundingClientRect();
        const containerWidth = rect.width;

        const MIN_LEFT = 180;
        const MAX_LEFT = 420;
        const MIN_RIGHT = 280;
        const MIN_CENTER = 420;

        if (isDraggingLeft) {
          const effRight = isRightCollapsed ? 0 : rightWidth;
          const maxAllowedLeft = Math.max(MIN_LEFT, containerWidth - effRight - MIN_CENTER);
          const raw = e.clientX - rect.left;
          const newW = Math.round(Math.min(Math.max(raw, MIN_LEFT), Math.min(MAX_LEFT, maxAllowedLeft)));
          setLeftWidth(newW);
        } else if (isDraggingRight) {
          const effLeft = isLeftCollapsed ? 0 : leftWidth;
          const maxAllowedRight = Math.max(MIN_RIGHT, containerWidth - effLeft - MIN_CENTER);
          const raw = rect.right - e.clientX;
          const newW = Math.round(Math.min(Math.max(raw, MIN_RIGHT), Math.min(maxAllowedRight, Math.floor(containerWidth * 0.72))));
          setRightWidth(newW);
        }
      });
    };

    const stopDragging = () => {
      if (animId) {
        cancelAnimationFrame(animId);
        animId = null;
      }
      setIsDraggingLeft(false);
      setIsDraggingRight(false);
      document.body.classList.remove('resizing-active');
    };

    window.addEventListener('pointermove', handlePointerMove, { passive: true });
    window.addEventListener('pointerup', stopDragging);
    window.addEventListener('pointercancel', stopDragging);

    return () => {
      if (animId) cancelAnimationFrame(animId);
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', stopDragging);
      window.removeEventListener('pointercancel', stopDragging);
      document.body.classList.remove('resizing-active');
    };
  }, [isDraggingLeft, isDraggingRight, isLeftCollapsed, isRightCollapsed, leftWidth, rightWidth]);

  // Responsive boundary safety on window resize
  useEffect(() => {
    const handleResize = () => {
      if (!layoutRef.current) return;
      const containerWidth = layoutRef.current.getBoundingClientRect().width;
      const MIN_CENTER = 360;
      const effLeft = isLeftCollapsed ? 0 : leftWidth;
      const effRight = isRightCollapsed ? 0 : rightWidth;

      if (effLeft + effRight + MIN_CENTER > containerWidth) {
        const maxRight = Math.max(280, containerWidth - effLeft - MIN_CENTER);
        if (rightWidth > maxRight && !isRightCollapsed) {
          setRightWidth(Math.round(maxRight));
        }
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [leftWidth, rightWidth, isLeftCollapsed, isRightCollapsed]);

  const loadWorkspaceData = async () => {
    try {
      const resFiles = await fetch('/api/workspace/files');
      if (resFiles.ok) {
        const data = await resFiles.json();
        setFiles(data.files || []);
      }

      const resManifest = await fetch('/api/workspace/manifest');
      if (resManifest.ok) {
        const data = await resManifest.json();
        setManifest(data);
      }

      const resHealth = await fetch('/api/workspace/health');
      if (resHealth.ok) {
        const data = await resHealth.json();
        setHealth(data);
      }

            try {
        const resTasks = await fetch('/api/tasks');
        if (resTasks.ok) {
          const tasksData = await resTasks.json();
          if (tasksData && tasksData.plan) {
            setActivePlan(tasksData.plan);
          }
        }
      } catch (err) {}

      const resProjects = await fetch('/api/projects');
      if (resProjects.ok) {
        const data = await resProjects.json();
        const projs = data.projects || [];
        setProjectsList(projs);
        if (projs.length > 0) {
          setPreviewProject((curr) => (!curr || !projs.some(p => p.name === curr) ? projs[0].name : curr));
          setPreviewStatus('ready');
        }
      }
    } catch (err) {
      console.error('Failed to load workspace data:', err);
    }
  };

  const handleIncomingEvent = (data) => {
    if (!data) return;

      const eventId = data.event_id || (data.event + '_' + (data.timestamp || '') + '_' + (data.task_id || '') + '_' + JSON.stringify(data.data || {}).slice(0, 40));
      if (processedEventsRef.current.has(eventId)) {
        return;
      }
      processedEventsRef.current.add(eventId);
      if (processedEventsRef.current.size > 1000) {
        const arr = Array.from(processedEventsRef.current);
        arr.slice(0, 200).forEach((id) => processedEventsRef.current.delete(id));
      }

      const eventType = data.event;

      if (eventType === 'run_started') {
        const rid = data.data?.run_id || data.run_id;
        if (rid) setCurrentRunId(rid);
        const pName = data.data?.project_name || data.project_name;
        if (pName) {
          setPreviewProject(pName);
          setPreviewStatus('building');
        }
      } else if (eventType === 'heartbeat' || eventType === 'agent_heartbeat') {
        const hb = data.data || data;
        setHeartbeat(hb);
        if (hb.latest_tool) {
          setTerminalLogs((prev) => [...prev.slice(-100), `⚡ Executing: ${hb.latest_tool}`]);
        }
      } else if (eventType === 'agent_thinking' || eventType === 'thinking_update') {
        const thought = data.data?.thought || data.data?.thinking || data.thought || data.thinking;
        if (thought) {
          setTerminalLogs((prev) => [...prev.slice(-100), `💭 ${thought}`]);
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg && lastMsg.sender === 'agent' && lastMsg.isStreaming) {
              lastMsg.thinking = (lastMsg.thinking ? lastMsg.thinking + '\n' : '') + thought;
            } else {
              updated.push({
                sender: 'agent',
                thinking: thought,
                content: '',
                isStreaming: true
              });
            }
            return updated;
          });
        }
      } else if (eventType === 'tool_invocation' || eventType === 'tool_started') {
        const toolName = data.data?.tool || data.data?.tool_name || data.tool || data.tool_name || 'tool';
        const toolArgs = data.data?.args || data.data?.arguments || data.args || data.arguments || {};
        setTerminalLogs((prev) => [...prev.slice(-100), `🔨 Tool: ${toolName}`]);
        setMessages((prev) => {
          const updated = [...prev];
          const lastMsg = updated[updated.length - 1];
          if (lastMsg && lastMsg.sender === 'agent') {
            if (!lastMsg.toolCalls) lastMsg.toolCalls = [];
            lastMsg.toolCalls.push({
              tool: toolName,
              args: toolArgs,
              status: 'running'
            });
          }
          return updated;
        });
      } else if (eventType === 'tool_output') {
        const toolName = data.data?.tool || data.tool || 'tool';
        const toolResult = data.data?.result || data.result;
        setTerminalLogs((prev) => [...prev.slice(-100), `✓ Finished: ${toolName}`]);
        setMessages((prev) => {
          const updated = [...prev];
          const lastMsg = updated[updated.length - 1];
          if (lastMsg && lastMsg.toolCalls && lastMsg.toolCalls.length > 0) {
            const tc = lastMsg.toolCalls.find(c => c.tool === toolName && c.status === 'running') || lastMsg.toolCalls[lastMsg.toolCalls.length - 1];
            if (tc) {
              tc.result = toolResult;
              tc.status = 'completed';
            }
          }
          return updated;
        });
      } else if (eventType === 'agent_message' || eventType === 'assistant_message') {
        const content = data.data?.content ?? data.content ?? '';
        const isDelta = data.data?.is_delta ?? false;
        if (content) {
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg && lastMsg.sender === 'agent' && lastMsg.isStreaming) {
              if (isDelta) {
                lastMsg.content = (lastMsg.content || '') + content;
              } else {
                lastMsg.content = content;
                lastMsg.isStreaming = false;
              }
            } else {
              updated.push({
                sender: 'agent',
                content: content,
                isStreaming: isDelta
              });
            }
            return updated;
          });
        }
      } else if (eventType === 'plan_created' || eventType === 'plan_updated') {
        const newPlan = data.data?.plan || data.plan;
        if (newPlan) {
          setActivePlan(newPlan);
          if (eventType === 'plan_created') {
            setMessages((prev) => [
              ...prev,
              {
                sender: 'agent',
                type: 'plan_created',
                plan: newPlan
              }
            ]);
          }
        }
      } else if (eventType === 'task_started') {
        const taskId = data.data?.task_id || data.task_id;
        const incomingPlan = data.data?.plan || data.plan;
        if (incomingPlan) {
          setActivePlan(incomingPlan);
        } else {
          setActivePlan((prev) => {
            if (!prev || !prev.tasks) return prev;
            return {
              ...prev,
              tasks: prev.tasks.map((t) => (t.id === taskId ? { ...t, status: 'IN_PROGRESS' } : t))
            };
          });
        }
      } else if (eventType === 'task_completed') {
        const taskId = data.data?.task_id || data.task_id;
        const incomingPlan = data.data?.plan || data.plan;
        if (incomingPlan) {
          setActivePlan(incomingPlan);
        } else {
          setActivePlan((prev) => {
            if (!prev || !prev.tasks) return prev;
            return {
              ...prev,
              tasks: prev.tasks.map((t) => (t.id === taskId ? { ...t, status: 'COMPLETED' } : t))
            };
          });
        }
      } else if (eventType === 'task_failed') {
        const taskId = data.data?.task_id || data.task_id;
        const errMsg = data.data?.error || data.error || 'Execution failed';
        setActivePlan((prev) => {
          if (!prev || !prev.tasks) return prev;
          return {
            ...prev,
            tasks: prev.tasks.map((t) => (t.id === taskId ? { ...t, status: 'FAILED', error_message: errMsg } : t))
          };
        });
      } else if (eventType === 'generation_status_update') {
        const updateData = data.data || data;
        const msg = updateData.message;
        const pct = updateData.progress_percent;
        if (msg) {
          setTerminalLogs((prev) => [...prev.slice(-100), `⚡ ${msg}`]);
        }
        setActivePlan((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            current_status_message: msg,
            overall_progress: pct
          };
        });
      } else if (eventType === 'project_build_completed') {
        const buildProjName = data.data?.project_name || data.project_name;
        const buildSuccess = data.data?.success ?? data.success ?? true;
        setMessages((prev) => [
          ...prev,
          {
            sender: 'agent',
            type: 'build_completion',
            project_name: buildProjName,
            project_directory: data.data?.project_directory || data.project_directory,
            files_created: data.data?.files_created || data.files_created,
            files_modified: data.data?.files_modified || data.files_modified,
            tests_executed: data.data?.tests_executed || data.tests_executed,
            test_results: data.data?.test_results || data.test_results,
            success: buildSuccess,
            remaining_issues: data.data?.remaining_issues || data.remaining_issues,
            preview_url: '/preview/' + buildProjName
          }
        ]);
        setPreviewProject(buildProjName);
        setPreviewStatus(buildSuccess ? 'ready' : 'failed');
        setTerminalLogs((prev) => [...prev.slice(-100), `${buildSuccess ? '✓' : '❌'} Build ${buildSuccess ? 'Finished' : 'Failed'}: ${buildProjName} (Status: ${buildSuccess ? 'Success' : 'Failed'})`]);
        loadWorkspaceData();
        setTimeout(() => {
          const sideIframe = document.getElementById('live-app-iframe-side');
          if (sideIframe) sideIframe.src = `/preview/${buildProjName}/?t=${Date.now()}`;
          const mainIframe = document.getElementById('full-app-preview-iframe');
          if (mainIframe) mainIframe.src = `/preview/${buildProjName}/?t=${Date.now()}`;
        }, 500);
      } else if (eventType === 'agent_finished' || eventType === 'turn_complete' || eventType === 'run_completed') {
        setIsProcessing(false);
        setActivePlan((prev) => {
          if (!prev || !prev.tasks) return prev;
          return {
            ...prev,
            tasks: prev.tasks.map((t) => ({ ...t, status: 'COMPLETED' })),
            overall_progress: 100
          };
        });
        setHeartbeat({ status: 'idle', elapsed_seconds: 0, latest_tool: null });
        setMessages((prev) =>
          prev.map((m, idx) => idx === prev.length - 1 ? { ...m, isStreaming: false } : m)
        );
        setPreviewStatus('ready');
        loadWorkspaceData();
        setTimeout(() => {
          const sideIframe = document.getElementById('live-app-iframe-side');
          if (sideIframe && previewProject) {
            sideIframe.src = '/preview/' + previewProject + '/?t=' + Date.now();
          }
        }, 400);
      } else if (eventType === 'project_selection_required') {
        const pList = data.data?.projects || [];
        const origPrompt = data.data?.prompt || '';
        setIsProcessing(false);
        setHeartbeat({ status: 'idle', elapsed_seconds: 0, latest_tool: null });
        setMessages((prev) => [
          ...prev,
          {
            sender: 'agent',
            type: 'project_selection_required',
            content: 'Multiple matching projects were found in your workspace. Select a project to continue, or create a new project:',
            projects: pList,
            prompt: origPrompt
          }
        ]);
      } else if (eventType === 'language_selection_required') {
        const pName = data.data?.project_name || 'temp_project';
        const origPrompt = data.data?.prompt || '';
        setIsProcessing(false);
        setHeartbeat({ status: 'idle', elapsed_seconds: 0, latest_tool: null });
        setMessages((prev) => [
          ...prev,
          {
            sender: 'agent',
            type: 'language_selection_required',
            content: 'Please select a programming language for this project:',
            project_name: pName,
            prompt: origPrompt
          }
        ]);
      } else if (eventType === 'provider_status') {
        const info = data.data || data;
        if (info.display_name) setActiveProvider(info.display_name);
        if (info.message) setTerminalLogs((prev) => [...prev.slice(-100), `⚡ ${info.message}`]);
      } else if (eventType === 'error') {
        const errMsg = data.data?.error || data.error || 'An unexpected error occurred.';
        setIsProcessing(false);
        setHeartbeat({ status: 'idle', elapsed_seconds: 0, latest_tool: null });
        setMessages((prev) => [
          ...prev.map((m, idx) => idx === prev.length - 1 ? { ...m, isStreaming: false } : m),
          {
            sender: 'agent',
            type: 'error',
            content: errMsg,
            isStreaming: false
          }
        ]);
        setTerminalLogs((prev) => [...prev.slice(-100), `❌ Error: ${errMsg}`]);
        setPreviewStatus('idle');
      } else if (eventType === 'approval_required') {
        setApprovalRequest(data.data || data);
      }
  };

  useEffect(() => {
    loadWorkspaceData();

    let isUnmounted = false;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      if (isUnmounted) return;
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      try {
        const socket = new WebSocket(wsUrl);
        wsRef.current = socket;
        window.__hermes_ws = socket;

        socket.onopen = () => {
          console.log('WebSocket connected to NEXARCH Agent server.');
          setTerminalLogs((prev) => [...prev.slice(-100), '⚡ Connected to NEXARCH Agent Server']);
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleIncomingEvent(data);
          } catch (err) {
            console.error('Error parsing WS message:', err);
          }
        };

        socket.onerror = (err) => {
          console.warn('WebSocket warning:', err);
        };

        socket.onclose = () => {
          if (!isUnmounted) {
            console.log('WebSocket disconnected. Reconnecting in 2.5s...');
            reconnectTimeout = setTimeout(connectWebSocket, 2500);
          }
        };
      } catch (wsErr) {
        console.error('Failed to initialize WebSocket:', wsErr);
        if (!isUnmounted) {
          reconnectTimeout = setTimeout(connectWebSocket, 3000);
        }
      }
    };

    connectWebSocket();

    return () => {
      isUnmounted = true;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleSelectFile = async (path) => {
    setSelectedFilePath(path);
    setActiveTab('editor');
    try {
      const res = await fetch(`/api/workspace/file?path=${encodeURIComponent(path)}`);
      if (res.ok) {
        const data = await res.json();
        setFileContent(data.content);
      }
    } catch (err) {
      console.error('Failed to load file:', err);
    }
  };

  const handleSaveFile = async () => {
    if (!selectedFilePath) return;
    try {
      const res = await fetch('/api/workspace/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: selectedFilePath, content: fileContent })
      });
      if (res.ok) {
        alert(`File saved: ${selectedFilePath}`);
        loadWorkspaceData();
      }
    } catch (err) {
      console.error('Failed to save file:', err);
    }
  };

  const handleSendMessage = async (textOrObj) => {
    setIsProcessing(true);
    setPreviewStatus('building');
    setHeartbeat({ status: 'working', elapsed_seconds: 0, latest_tool: null });
    const userStr = typeof textOrObj === 'string' ? textOrObj : (textOrObj.content || 'Action requested');
    setTerminalLogs((prev) => [...prev.slice(-100), `> ${userStr}`]);
    
    const msgContent = typeof textOrObj === 'object' 
      ? (textOrObj.type === 'project_selected' ? `Switched to project ${textOrObj.project_name}` : textOrObj.content)
      : textOrObj;
    setMessages((prev) => [...prev, { sender: 'user', content: msgContent }]);

    const payload = typeof textOrObj === 'object' ? textOrObj : { type: 'user_message', content: textOrObj };
    let sentViaWs = false;

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(payload));
        sentViaWs = true;
      } catch (wsErr) {
        console.warn('WebSocket send failed, will use HTTP fallback:', wsErr);
      }
    }

    if (!sentViaWs) {
      console.log('Sending message via HTTP POST /api/chat fallback...');
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: currentRunId || 'session_user',
            message: userStr
          })
        });
        if (res.ok) {
          const resData = await res.json();
          if (resData.events && Array.isArray(resData.events)) {
            resData.events.forEach((evt) => handleIncomingEvent(evt));
          }
        } else {
          const errText = await res.text();
          throw new Error(errText || 'Chat endpoint returned error');
        }
      } catch (httpErr) {
        console.error('HTTP chat error:', httpErr);
        setIsProcessing(false);
        setHeartbeat({ status: 'idle', elapsed_seconds: 0, latest_tool: null });
        setMessages((prev) => [
          ...prev,
          { sender: 'agent', type: 'error', content: `Request failed: ${httpErr.message || 'Unable to connect to server'}` }
        ]);
        setTerminalLogs((prev) => [...prev.slice(-100), `❌ Request failed: ${httpErr.message}`]);
      }
    }
  };

  const handleInitiateDelete = (projectName, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    setProjectToDelete(projectName);
  };

  const handleConfirmDelete = async () => {
    if (!projectToDelete) return;
    setIsDeletingProject(true);
    try {
      const res = await fetch(`/api/projects/${encodeURIComponent(projectToDelete)}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        if (previewProject === projectToDelete) {
          setPreviewProject(null);
          setPreviewStatus('idle');
        }
        await loadWorkspaceData();
        setTerminalLogs((prev) => [...prev.slice(-100), `🗑️ Project "${projectToDelete}" permanently deleted.`]);
        setProjectToDelete(null);
      } else {
        const err = await res.json().catch(() => ({}));
        alert(`Failed to delete project: ${err.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Failed to delete project:', err);
      alert('Failed to delete project.');
    } finally {
      setIsDeletingProject(false);
    }
  };

  const handleResolveApproval = async (requestId, approved) => {
    try {
      await fetch('/api/approval/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: requestId, approved })
      });
      setApprovalRequest(null);
    } catch (err) {
      console.error('Failed to resolve approval:', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* 1. Global Header Navbar (No provider or model labels visible) */}
      <header className="app-header">
        <div className="header-left">
          <button 
            className={`header-icon-btn ${isLeftCollapsed ? 'panel-toggle-collapsed' : ''}`}
            onClick={() => setIsLeftCollapsed(prev => !prev)}
            title={isLeftCollapsed ? "Expand sidebar (⌘B)" : "Collapse sidebar (⌘B)"}
            aria-label={isLeftCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isLeftCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
          </button>

          <div className="brand-logo">
            <div className="brand-icon-box">
              <NexarchLogo size={24} theme={theme} />
            </div>
            <div className="brand-title-group">
              <div className="brand-title">NEXARCH</div>
              <div className="brand-subtitle">INTELLIGENCE, ARCHITECTED.</div>
            </div>
          </div>

          <div className="status-pills">
            <span className="pill-badge">
              <span className="pill-status-dot"></span> Online
            </span>
          </div>
        </div>

        {/* Center Segmented Navigation Pills */}
        <div className="header-center-nav">
          <button 
            className={`nav-pill-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Workspace
          </button>
          <button 
            className={`nav-pill-btn ${activeTab === 'editor' ? 'active' : ''}`}
            onClick={() => setActiveTab('editor')}
          >
            Code
          </button>
          <button 
            className={`nav-pill-btn ${activeTab === 'plan' ? 'active' : ''}`}
            onClick={() => setActiveTab('plan')}
          >
            Execution Plan
          </button>
          <button 
            className={`nav-pill-btn ${activeTab === 'preview' ? 'active' : ''}`}
            onClick={() => setActiveTab('preview')}
          >
            Preview
          </button>
          <button 
            className={`nav-pill-btn ${activeTab === 'downloads' ? 'active' : ''}`}
            onClick={() => setActiveTab('downloads')}
          >
            Archive
          </button>
        </div>

        {/* Right Toolbar */}
        <div className="header-right">
          <button 
            className={`header-icon-btn ${isRightCollapsed ? 'panel-toggle-collapsed' : ''}`}
            onClick={() => setIsRightCollapsed(prev => !prev)}
            title={isRightCollapsed ? "Expand preview panel (⌘\)" : "Collapse preview panel (⌘\)"}
            aria-label={isRightCollapsed ? "Expand preview panel" : "Collapse preview panel"}
          >
            {isRightCollapsed ? <PanelRightOpen size={16} /> : <PanelRightClose size={16} />}
          </button>
          <button className="header-icon-btn" title="Search"><Search size={15} /></button>
          <button className="header-icon-btn" title="Notifications"><Bell size={15} /></button>
          <button 
            className="header-icon-btn" 
            title="Toggle Theme"
            onClick={() => setTheme(prev => prev === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </header>

      {/* Main Studio Body with 3 Resizable Columns */}
      <div 
        ref={layoutRef}
        className="studio-body-layout" 
        style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative', width: '100%' }}
      >
        {/* Full-screen Drag Overlay preventing iframe pointer absorption */}
        {(isDraggingLeft || isDraggingRight) && (
          <div 
            className="resize-drag-overlay"
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 99999,
              cursor: 'col-resize',
              userSelect: 'none',
              background: 'transparent'
            }}
          />
        )}
        
        {/* Left Resizable & Collapsible Sidebar */}
        <aside 
          className={`left-sidebar ${isLeftCollapsed ? 'collapsed' : ''}`} 
          style={{ 
            width: isLeftCollapsed ? 0 : `${leftWidth}px`, 
            minWidth: isLeftCollapsed ? 0 : '180px',
            maxWidth: '450px'
          }}
        >
          {/* Sidebar Top Header with Title and Collapse Button */}
          <div className="sidebar-top-bar">
            <span className="sidebar-top-label">Workspace</span>
            <button
              className="sidebar-collapse-trigger"
              onClick={() => setIsLeftCollapsed(true)}
              title="Collapse sidebar (⌘B)"
              aria-label="Collapse sidebar"
            >
              <PanelLeftClose size={15} />
            </button>
          </div>

          <button 
            className="btn-new-project"
            onClick={() => {
              setPreviewProject(null);
              setPreviewStatus('idle');
              handleSendMessage("Create a new software project");
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Plus size={15} /> New Project
            </span>
            <span className="shortcut-kbd">⌘N</span>
          </button>

          <div className="sidebar-nav-group">
            <div className={`sidebar-nav-item ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
              <Box size={16} /> Workspace
            </div>
            <div className={`sidebar-nav-item ${activeTab === 'editor' ? 'active' : ''}`} onClick={() => setActiveTab('editor')}>
              <Code size={16} /> Code Editor
            </div>
            <div className={`sidebar-nav-item ${activeTab === 'plan' ? 'active' : ''}`} onClick={() => setActiveTab('plan')}>
              <CheckSquare size={16} /> Execution Plan
            </div>
            <div className={`sidebar-nav-item ${activeTab === 'preview' ? 'active' : ''}`} onClick={() => setActiveTab('preview')}>
              <Eye size={16} /> Preview
            </div>
            <div className={`sidebar-nav-item ${activeTab === 'downloads' ? 'active' : ''}`} onClick={() => setActiveTab('downloads')}>
              <Download size={16} /> Archive
            </div>
          </div>

          <div style={{ marginTop: '0.5rem', flex: 1, overflowY: 'auto' }}>
            <div className="sidebar-section-title">Recent Projects</div>
            <div className="recent-projects-list">
              {projectsList.length > 0 ? (
                projectsList.map((proj) => {
                  const isActive = previewProject === proj.name;
                  const isRunning = proj.status === 'Running' || proj.status === 'Active';
                  return (
                    <div 
                      key={proj.name}
                      className={`project-item ${isActive ? 'active' : ''}`}
                      onClick={() => {
                        setPreviewProject(proj.name);
                        setPreviewStatus('ready');
                      }}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'space-between' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden', flex: 1 }}>
                        <div className="project-item-icon">{proj.name.charAt(0).toUpperCase()}</div>
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {proj.name}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', flexShrink: 0 }}>
                        {isRunning ? (
                          <span className="status-badge-ready">• Running</span>
                        ) : (
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Ready</span>
                        )}
                        <button
                          className="btn-sidebar-delete"
                          onClick={(e) => handleInitiateDelete(proj.name, e)}
                          title={`Delete ${proj.name}`}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--text-dim)',
                            cursor: 'pointer',
                            padding: '3px 4px',
                            borderRadius: '4px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            opacity: 0.6,
                            transition: 'opacity 0.15s, color 0.15s'
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.opacity = '1'; }}
                          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-dim)'; e.currentTarget.style.opacity = '0.6'; }}
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', padding: '0.5rem 0.2rem' }}>
                  No recent projects created yet.
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* Resizable Vertical Drag Handle (Left) */}
        {!isLeftCollapsed && (
          <div 
            className={`splitter-handle-v ${isDraggingLeft ? 'dragging' : ''}`}
            onPointerDown={(e) => { e.preventDefault(); setIsDraggingLeft(true); }}
            onDoubleClick={() => setLeftWidth(250)}
            title="Drag to resize sidebar • Double-click to reset"
            aria-label="Resize left sidebar"
            role="separator"
            aria-orientation="vertical"
          />
        )}

        {/* Center Main Workspace / Canvas (MANDATORY & NEVER COLLAPSIBLE) */}
        <main className="center-workspace" style={{ flex: '1 1 0%', minWidth: 0, position: 'relative' }}>
          {/* Floating quick-restore pills when side panels are collapsed */}
          {isLeftCollapsed && (
            <button
              className="canvas-restore-pill restore-pill-left"
              onClick={() => setIsLeftCollapsed(false)}
              title="Expand sidebar (⌘B)"
              aria-label="Expand sidebar"
            >
              <PanelLeftOpen size={14} />
              <span>Sidebar</span>
            </button>
          )}

          {isRightCollapsed && (
            <button
              className="canvas-restore-pill restore-pill-right"
              onClick={() => setIsRightCollapsed(false)}
              title="Expand preview panel (⌘\)"
              aria-label="Expand preview panel"
            >
              <PanelRightOpen size={14} />
              <span>Preview</span>
            </button>
          )}

          {activeTab === 'chat' && (
            <ChatPanel 
              messages={messages} 
              onSendMessage={handleSendMessage} 
              isProcessing={isProcessing}
              activeProvider={activeProvider}
              currentRunId={currentRunId} 
              heartbeat={heartbeat} 
              onRefreshWorkspace={loadWorkspaceData} 
              onOpenPreview={(projName) => {
                if (projName) setPreviewProject(projName);
                setPreviewStatus('ready');
                setActiveTab('preview');
              }}
            />
          )}

          {activeTab === 'editor' && (
            <div style={{ background: 'var(--bg-card)', borderRadius: '16px', border: '1px solid var(--border-color)', height: '100%', display: 'flex', flex: 1, overflow: 'hidden' }}>
              <div style={{ width: '220px', borderRight: '1px solid var(--border-color)', background: 'var(--bg-panel)' }}>
                <FileTree files={files} onSelectFile={handleSelectFile} selectedFile={selectedFilePath} />
              </div>
              <div style={{ flex: 1 }}>
                <FileViewer
                  path={selectedFilePath}
                  content={fileContent}
                  onChange={setFileContent}
                  onSave={handleSaveFile}
                />
              </div>
            </div>
          )}

          {activeTab === 'plan' && (
            <div style={{ background: 'var(--bg-card)', borderRadius: '16px', border: '1px solid var(--border-color)', padding: '1.5rem', height: '100%', overflowY: 'auto' }}>
              <PlanView plan={activePlan} onGoToChat={() => setActiveTab('chat')} />
            </div>
          )}

          {activeTab === 'preview' && (
            <div style={{ background: 'var(--bg-card)', borderRadius: '16px', border: '1px solid var(--border-color)', height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '0.65rem 1rem', background: 'var(--bg-panel)', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-heading)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Eye size={16} /> Live Preview {previewProject ? ` - ${previewProject}` : ''}
                </div>
                {previewProject && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <a
                      href={`/preview/${previewProject}/`}
                      target="_blank"
                      rel="noreferrer"
                      className="download-btn-primary"
                    >
                      Open New Tab <ExternalLink size={13} />
                    </a>
                  </div>
                )}
              </div>
              <div style={{ flex: 1, position: 'relative' }}>
                {previewProject && previewStatus === 'ready' ? (
                  <iframe
                    id="full-app-preview-iframe"
                    src={`/preview/${previewProject}/`}
                    title="Full Live App Preview"
                    style={{ width: '100%', height: '100%', border: 'none', background: '#FFFFFF' }}
                  />
                ) : isProcessing || previewStatus === 'building' ? (
                  <div className="preview-state-card">
                    <Loader2 size={36} className="animate-spin" style={{ color: 'var(--accent-gold)' }} />
                    <div className="preview-state-title">Building Your Application...</div>
                    <div className="preview-state-subtitle">NEXARCH is actively setting up files, dependencies, and compilation servers.</div>
                  </div>
                ) : (
                  <div className="preview-state-card">
                    <Box size={42} style={{ color: 'var(--text-dim)' }} />
                    <div className="preview-state-title">Your Application Preview Will Appear Here</div>
                    <div className="preview-state-subtitle">Start by asking NEXARCH to build a project using the prompt composer.</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'downloads' && (
            <div style={{ background: 'var(--bg-card)', borderRadius: '16px', border: '1px solid var(--border-color)', padding: '1.75rem', height: '100%', overflowY: 'auto' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.3rem', color: 'var(--text-heading)', marginBottom: '0.5rem' }}>
                Built Project Archives
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                Download compiled standalone project packages generated by NEXARCH Agent.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {projectsList.length > 0 ? (
                  projectsList.map((proj) => (
                    <div key={proj.name} style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--text-heading)' }}>📦 {proj.name}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>workspace/{proj.name}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <a href={proj.download_url || `/api/projects/${proj.name}/download`} download className="download-btn-primary">
                          <Download size={14} /> ZIP Archive
                        </a>
                        <button 
                          className="btn-delete-project"
                          onClick={(e) => handleInitiateDelete(proj.name, e)}
                          title={`Delete ${proj.name}`}
                          style={{
                            background: 'rgba(239, 68, 68, 0.08)',
                            color: '#ef4444',
                            border: '1px solid rgba(239, 68, 68, 0.25)',
                            borderRadius: '8px',
                            padding: '0.45rem 0.75rem',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            transition: 'all 0.15s ease'
                          }}
                        >
                          <Trash2 size={13} /> Delete
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    No standalone project packages generated yet.
                  </div>
                )}
              </div>
            </div>
          )}
        </main>

        {/* Resizable Vertical Drag Handle (Right) */}
        {!isRightCollapsed && (
          <div 
            className={`splitter-handle-v ${isDraggingRight ? 'dragging' : ''}`}
            onPointerDown={(e) => { e.preventDefault(); setIsDraggingRight(true); }}
            onDoubleClick={() => setRightWidth(450)}
            title="Drag to resize preview • Double-click to reset"
            aria-label="Resize right preview"
            role="separator"
            aria-orientation="vertical"
          />
        )}

        {/* 3. Right Resizable & Collapsible Preview Panel */}
        <aside 
          className={`right-panel ${isRightCollapsed ? 'collapsed' : ''}`} 
          style={{ 
            width: isRightCollapsed ? 0 : `${rightWidth}px`, 
            minWidth: isRightCollapsed ? 0 : '280px' 
          }}
        >
          {/* Live Preview Panel */}
          <div className="preview-section">
            <div className="preview-toolbar">
              <div className="preview-title-group" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Eye size={15} />
                <select
                  value={previewProject || ''}
                  onChange={(e) => {
                    const selected = e.target.value;
                    if (selected) {
                      setPreviewProject(selected);
                      setPreviewStatus('ready');
                    }
                  }}
                  style={{
                    background: 'var(--bg-panel)',
                    color: 'var(--text-heading)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    padding: '0.2rem 0.4rem',
                    fontSize: '0.8rem',
                    fontWeight: 800,
                    cursor: 'pointer',
                    maxWidth: '160px'
                  }}
                >
                  {projectsList.length > 0 ? (
                    projectsList.map((p) => (
                      <option key={p.name} value={p.name}>
                        {p.name}
                      </option>
                    ))
                  ) : (
                    <option value="">No Projects</option>
                  )}
                </select>
                {previewProject && previewStatus === 'ready' && <span className="status-badge-ready">• Live</span>}
              </div>
              <div className="preview-viewport-actions">
                <button className="viewport-btn" title="Desktop View"><Box size={14} /></button>
                <button className="viewport-btn" title="Tablet View"><Box size={13} /></button>
                <button className="viewport-btn" title="Mobile View"><Box size={12} /></button>
                {previewProject && (
                  <button 
                    className="viewport-btn" 
                    title="Reload Preview"
                    onClick={() => {
                      const iframe = document.getElementById('live-app-iframe-side');
                      if (iframe) iframe.src = '/preview/' + previewProject + '/?t=' + Date.now();
                    }}
                  >
                    <RefreshCw size={13} />
                  </button>
                )}
                <button 
                  className="viewport-btn preview-collapse-trigger" 
                  title="Collapse preview panel (⌘\)"
                  aria-label="Collapse preview panel"
                  onClick={() => setIsRightCollapsed(true)}
                >
                  <PanelRightClose size={14} />
                </button>
              </div>
            </div>

            <div className="preview-url-bar">
              <div className="url-input-field">
                {previewProject ? `http://localhost:8000/preview/${previewProject}/` : 'No active preview'}
              </div>
              {previewProject && (
                <a 
                  href={`/preview/${previewProject}/`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ color: 'var(--text-muted)' }}
                  title="Open in new browser tab"
                >
                  <ExternalLink size={14} />
                </a>
              )}
            </div>

            <div className="preview-iframe-container">
              {previewProject && previewStatus === 'ready' ? (
                <iframe
                  id="live-app-iframe-side"
                  src={`/preview/${previewProject}/`}
                  title="Side Live Preview"
                  style={{ width: '100%', height: '100%', border: 'none', background: '#ffffff' }}
                />
              ) : isProcessing || previewStatus === 'building' ? (
                <div className="preview-state-card">
                  <Loader2 size={28} className="animate-spin" style={{ color: 'var(--accent-gold)' }} />
                  <div className="preview-state-title" style={{ fontSize: '0.92rem' }}>Building Application...</div>
                  <div className="preview-state-subtitle" style={{ fontSize: '0.75rem' }}>Setting up dependencies & compilation.</div>
                </div>
              ) : (
                <div className="preview-state-card">
                  <Box size={32} style={{ color: 'var(--text-dim)' }} />
                  <div className="preview-state-title" style={{ fontSize: '0.92rem' }}>Your Preview Will Appear Here</div>
                  <div className="preview-state-subtitle" style={{ fontSize: '0.75rem' }}>Ask NEXARCH to build a project to start.</div>
                </div>
              )}
            </div>
          </div>


        </aside>
      </div>

      {/* Custom In-App Delete Confirmation Modal (Persistent until user choice) */}
      {projectToDelete && (
        <div 
          className="modal-backdrop-custom"
          onClick={() => !isDeletingProject && setProjectToDelete(null)}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 99999,
            backgroundColor: 'rgba(0, 0, 0, 0.72)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem'
          }}
        >
          <div 
            className="delete-modal-card"
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: 'var(--bg-panel, #14151a)',
              border: '1px solid rgba(239, 68, 68, 0.35)',
              boxShadow: '0 24px 50px rgba(0,0,0,0.6), 0 0 0 1px rgba(239, 68, 68, 0.15)',
              borderRadius: '16px',
              padding: '1.75rem',
              maxWidth: '460px',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: '1.1rem',
              color: 'var(--text-main, #e5e5e5)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              <div 
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(239, 68, 68, 0.12)',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ef4444',
                  flexShrink: 0
                }}
              >
                <Trash2 size={22} />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-heading, #ffffff)' }}>
                  Delete Project
                </h3>
                <p style={{ margin: '0.2rem 0 0', fontSize: '0.78rem', color: 'var(--text-muted, #888)' }}>
                  Permanent, irreversible action
                </p>
              </div>
            </div>

            <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.55', color: 'var(--text-main, #d1d5db)' }}>
              Are you sure you want to permanently delete <strong style={{ color: 'var(--text-heading, #ffffff)', fontFamily: 'monospace', background: 'var(--bg-input, #1e2029)', padding: '0.2rem 0.45rem', borderRadius: '4px', border: '1px solid var(--border-color, #333)' }}>{projectToDelete}</strong>?
            </p>
            <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-dim, #9ca3af)', lineHeight: '1.45' }}>
              This will remove all workspace source code, assets, and compiled archives from the disk.
            </p>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button
                type="button"
                disabled={isDeletingProject}
                onClick={() => setProjectToDelete(null)}
                style={{
                  background: 'var(--bg-input, #222)',
                  border: '1px solid var(--border-color, #444)',
                  color: 'var(--text-main, #eee)',
                  borderRadius: '8px',
                  padding: '0.55rem 1.15rem',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  cursor: isDeletingProject ? 'not-allowed' : 'pointer',
                  transition: 'background 0.15s ease'
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isDeletingProject}
                onClick={handleConfirmDelete}
                style={{
                  background: '#ef4444',
                  border: '1px solid #dc2626',
                  color: '#ffffff',
                  borderRadius: '8px',
                  padding: '0.55rem 1.25rem',
                  fontSize: '0.85rem',
                  fontWeight: 800,
                  cursor: isDeletingProject ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  boxShadow: '0 4px 14px rgba(239, 68, 68, 0.4)',
                  transition: 'transform 0.1s ease, filter 0.15s ease'
                }}
              >
                {isDeletingProject ? (
                  <>
                    <Loader2 size={15} className="animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 size={15} />
                    Delete Permanently
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Security Approval Modal */}
      <ApprovalModal request={approvalRequest} onResolve={handleResolveApproval} />
    </div>
  );
}
