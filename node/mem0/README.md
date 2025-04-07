# Mem0 Memory Tool

A Model Context Protocol (MCP) server that provides memory storage and retrieval capabilities using [Mem0](https://github.com/mem0ai/mem0). This tool allows you to store and search through memories, making it useful for maintaining context and making informed decisions based on past interactions.

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

## Prerequisites

- Node.js (v14 or higher)
- A Mem0 API key [(Get Here)](https://app.mem0.ai/dashboard/api-keys)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory and add your Mem0 API key and user ID:
```bash
MEM0_API_KEY=your-api-key-here
DEFAULT_USER_ID=<your-user-id>
```


## Development

To run the server in development mode:

```bash
npm run dev
```

## Building

To build the project:

```bash
npm run build
```



## License

MIT 