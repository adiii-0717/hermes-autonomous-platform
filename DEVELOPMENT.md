# Developer & Extension Guide

> **Product**: Hermes Software Development Agent  
> **Framework**: NousResearch/hermes-agent

---

## 1. Project Layout

```text
├── server/
│   ├── main.py                   # FastAPI REST & WebSocket server
│   ├── hermes_adapter.py         # Hermes Agent runtime engine adapter
│   ├── security/
│   │   ├── workspace_guard.py    # Symlink & path traversal security boundary
│   │   └── approval_controller.py# Human-in-the-loop security approval manager
│   └── tools/
│       ├── dev_file_tools.py     # File manipulation tools
│       ├── dev_terminal_tools.py # Shell command execution & process backgrounding
│       ├── dev_testing_tools.py  # Test suite, linter, and build runners
│       └── dev_git_tools.py      # Git status, diff, and commit tools
├── client/
│   ├── src/                      # React frontend components & CSS design system
│   └── vite.config.js            # Vite development server configuration
└── tests/
    ├── test_security.py          # Security boundary & traversal unit tests
    ├── test_tools.py             # Development tool unit tests
    ├── test_api.py               # REST API unit tests
    └── test_e2e_scenarios.py     # 3 real End-to-End software development task scenarios
```

---

## 2. Adding Custom Development Tools

To add a new development tool for Hermes:

1. Create or update a tool class in `server/tools/`.
2. Register the tool in `server/hermes_adapter.py` inside `register_custom_tools_into_hermes()`:

```python
registry.register(
    name="my_custom_tool",
    toolset="development",
    schema={
        "name": "my_custom_tool",
        "description": "Description of custom tool.",
        "parameters": {"type": "object", "properties": {}}
    },
    handler=my_handler_function,
    is_async=False,
    override=True
)
```

3. Add corresponding unit tests in `tests/test_tools.py`.
