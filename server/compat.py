"""Product layer runtime compatibility adapters.

Ensures underlying Hermes framework and dependencies operate seamlessly across
different Python runtime environments (including Python 3.14+) without modifying
the core Hermes Agent codebase.
"""

import inspect
import threading
import weakref
from concurrent.futures.thread import _worker

def apply_python314_compat():
    """Applies Python 3.14 compatibility patch to DaemonThreadPoolExecutor at runtime."""
    try:
        import tools.daemon_pool
        sig_params = list(inspect.signature(_worker).parameters.keys())
        
        if sig_params == ["executor_reference", "ctx", "work_queue"]:
            def _compat_adjust_thread_count(self) -> None:
                if self._idle_semaphore.acquire(timeout=0):
                    return

                def weakref_cb(_, q=self._work_queue):
                    q.put(None)

                num_threads = len(self._threads)
                if num_threads < self._max_workers:
                    thread_name = "%s_%d" % (self._thread_name_prefix or self, num_threads)
                    worker_args = (
                        weakref.ref(self, weakref_cb),
                        self._create_worker_context() if hasattr(self, '_create_worker_context') else None,
                        self._work_queue
                    )
                    t = threading.Thread(
                        name=thread_name,
                        target=_worker,
                        args=worker_args,
                        daemon=True,
                    )
                    t.start()
                    self._threads.add(t)

            tools.daemon_pool.DaemonThreadPoolExecutor._adjust_thread_count = _compat_adjust_thread_count
    except ImportError:
        pass

# Automatically apply compatibility patches when server.compat is imported
apply_python314_compat()
