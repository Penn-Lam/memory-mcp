import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { MemoryClient } from 'mem0ai';
import * as dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

const MEM0_API_KEY = process?.env?.MEM0_API_KEY || '';
const DEFAULT_USER_ID = process?.env?.DEFAULT_USER_ID || 'default_user';

console.error('使用的用户 ID:', DEFAULT_USER_ID);

// 初始化mem0ai客户端
const memoryClient = new MemoryClient({ apiKey: MEM0_API_KEY });

// 创建服务器实例
const server = new McpServer({
  name: "memory-mcp",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  },
});

// 添加记忆的辅助函数
async function addMemory(content: string) {
  try {
    await memoryClient.add(content, { user_id: DEFAULT_USER_ID });
    return `成功添加记忆: ${content}`;
  } catch (error) {
    console.error("添加记忆时出错:", error);
    return `添加记忆时出错: ${error}`;
  }
}

// 搜索记忆的辅助函数
async function searchMemories(query: string) {
  try {
    const results = await memoryClient.search(query, { user_id: DEFAULT_USER_ID, limit: 5 });
    // 返回统一格式，确保有 results 属性
    return Array.isArray(results) ? { results } : results;
  } catch (error) {
    console.error("搜索记忆时出错:", error);
    return { results: [] };
  }
}

// 获取所有记忆的辅助函数
async function getAllMemories() {
  try {
    const memories = await memoryClient.getAll({ user_id: DEFAULT_USER_ID, page: 1, page_size: 50 });
    // 返回统一格式，确保有 results 属性
    return Array.isArray(memories) ? { results: memories } : memories;
  } catch (error) {
    console.error("获取记忆时出错:", error);
    return { results: [] };
  }
}

// 删除记忆的辅助函数
async function deleteMemory(memoryId: string) {
  try {
    await memoryClient.delete(memoryId);
    return `成功删除记忆 ID: ${memoryId}`;
  } catch (error) {
    console.error("删除记忆时出错:", error);
    return `删除记忆时出错: ${error}`;
  }
}

// 更新记忆的辅助函数
async function updateMemory(memoryId: string, newContent: string) {
  try {
    await memoryClient.update(memoryId, newContent);
    return `成功更新记忆 ID: ${memoryId}`;
  } catch (error) {
    console.error("更新记忆时出错:", error);
    return `更新记忆时出错: ${error}`;
  }
}

// 添加对话记忆的辅助函数
async function addConversationMemory(messages: any[]) {
  try {
    await memoryClient.add(messages, { user_id: DEFAULT_USER_ID });
    return "成功添加对话记忆";
  } catch (error) {
    console.error("添加对话记忆时出错:", error);
    return `添加对话记忆时出错: ${error}`;
  }
}

// 注册记忆工具
server.tool(
  "add-memory",
  `Add a new memory. 
  This method is called everytime the user informs anything about themselves, their preferences, 
  or anything that has any relevent information whcih can be useful in the future conversation. 
  This can also be called when the user asks you to remember something.
  IMPORTANT: 'content' must be the exact original message sent by the user. 
  DO NOT rewrite or rephrase it to third person. Keep it in first person as the user said it.
  Example: If user says "I like coffee", store "I like coffee" NOT "User likes coffee".`,
  {
    content: z.string().describe("The content to store in memory"),
  },
  async ({ content }) => {
    const result = await addMemory(content);
    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  },
);

server.tool(
  "search-memories",
  "Search through stored memories. This method is called ANYTIME the user asks anything.",
  {
    query: z.string().describe("The search query. This is the query that the user has asked for. Example: 'What did I tell you about the weather last week?' or 'What did I tell you about my friend John?'"),
  },
  async ({ query }) => {
    const memories = await searchMemories(query);
    
    if (!memories || !memories.results || memories.results.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: "未找到相关记忆。",
          },
        ],
      };
    }
    
    const results = memories.results.map((result: any, index: number) => {
      const memory_content = result.memory || "";
      const score = result.score || 0;
      return `${index + 1}. ${memory_content} (相关度: ${score.toFixed(4)})`;
    });
    
    return {
      content: [
        {
          type: "text",
          text: "找到以下相关记忆:\n" + results.join("\n"),
        },
      ],
    };
  },
);

server.tool(
  "get-all-memories",
  "Get all memories for a specific user. This provides a complete view of all stored information about the user.",
  {},
  async () => {
    const memories = await getAllMemories();
    
    if (!memories || !memories.results || memories.results.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: "该用户没有存储的记忆。",
          },
        ],
      };
    }
    
    const results = memories.results.map((memory: any, index: number) => {
      const memory_content = memory.memory || "";
      const created_at = memory.created_at || "";
      return `${index + 1}. ${memory_content}\n   创建时间: ${created_at}`;
    });
    
    return {
      content: [
        {
          type: "text",
          text: `用户 ${DEFAULT_USER_ID} 的所有记忆:\n` + results.join("\n"),
        },
      ],
    };
  },
);

server.tool(
  "delete-memory",
  "Delete a specific memory by its ID. Use this when information is no longer relevant or needs to be removed.",
  {
    memoryId: z.string().describe("The ID of the memory to delete"),
  },
  async ({ memoryId }) => {
    const result = await deleteMemory(memoryId);
    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  },
);

server.tool(
  "update-memory",
  "Update an existing memory with new content. Use this to modify or correct previously stored information.",
  {
    memoryId: z.string().describe("The ID of the memory to update"),
    newContent: z.string().describe("The new content for the memory"),
  },
  async ({ memoryId, newContent }) => {
    const result = await updateMemory(memoryId, newContent);
    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  },
);

server.tool(
  "add-conversation-memory",
  "Add a conversation as memory. This stores an entire conversation thread between the user and assistant.",
  {
    messages: z.array(z.object({
      role: z.string().describe("The role of the message sender (user or assistant)"),
      content: z.string().describe("The content of the message")
    })).describe("The conversation messages to store"),
  },
  async ({ messages }) => {
    const result = await addConversationMemory(messages);
    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  },
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("记忆 MCP 服务器运行在 stdio 上");
}

main().catch((error) => {
  console.error("main() 中出现致命错误:", error);
  process.exit(1);
});