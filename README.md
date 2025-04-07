# MCP Server with Mem0 for Managing Memory

This demonstrates a structured approach for using an [MCP](https://modelcontextprotocol.io/introduction) server with [mem0](https://mem0.ai) to manage Memory from different sources efficiently. 
## Installation

1. Clone this repository
2. Initialize the `uv` environment:

```bash
uv venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`:

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Update `.env` file in the root directory with your mem0 API key:

```bash
MEM0_API_KEY=your_api_key_here
```

## Usage

1. Start the MCP server:

```bash
uv run main.py
```

2. In MCP Client, connect to the SSE endpoint:

```
http://0.0.0.0:8080/sse
```


## Features

The server provides comprehensive tools for managing Memory:

1. `add_memory`: Store user information, preferences and important details
- Stores the exact original message from users (first-person format)
- Captures personal preferences and habits
- Stores any relevant information for future conversations
- Preserves context exactly as provided by the user

2. `search_memories`: Find relevant memories using semantic search
- Natural language understanding for flexible queries
- Returns memories ranked by relevance
- Useful for retrieving context before responding to users
- Supports finding related information across different topics

3. `get_all_memories`: View complete memory history
- Retrieves all stored memories for a user
- Includes creation timestamps for each memory
- Provides full context of user interactions
- Useful for analyzing memory patterns

4. `delete_memory`: Remove specific memories
- Delete memories by ID when no longer relevant
- Maintain memory accuracy by removing outdated information
- Supports GDPR compliance and privacy requests

5. `update_memory`: Modify existing memories
- Correct or update stored information
- Keep memories current and accurate
- Preserve memory IDs while updating content

6. `add_conversation_memory`: Store complete conversations
- Captures full dialog context between user and assistant
- Stores message history with roles (user/assistant)
- Preserves conversation flow for future reference
- Useful for maintaining continuity in long-running conversations


## Why?

This implementation allows for a persistent coding preferences system that can be accessed via MCP. The SSE-based server can run as a process that agents connect to, use, and disconnect from whenever needed. This pattern fits well with "cloud-native" use cases where the server and clients can be decoupled processes on different nodes.

### Server

By default, the server runs on 0.0.0.0:8080 but is configurable with command line arguments like:

```
uv run main.py --host <your host> --port <your port>
```

The server exposes an SSE endpoint at `/sse` that MCP clients can connect to for accessing the coding preferences management tools.

