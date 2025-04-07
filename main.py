from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
import os

# 加载环境变量
load_dotenv()

# 初始化FastMCP服务器
mcp = FastMCP("memory-mcp")

# 初始化mem0客户端
mem0_client = MemoryClient()
DEFAULT_USER_ID = os.environ.get("DEFAULT_USER_ID", "default_user")

@mcp.tool(
    description="""
    Add a new memory. 
    This method is called everytime the user informs anything about themselves, their preferences, 
    or anything that has any relevent information whcih can be useful in the future conversation. 
    This can also be called when the user asks you to remember something.
    IMPORTANT: `content` must be the exact original message sent by the user. 
    DO NOT rewrite or rephrase it to third person. Keep it in first person as the user said it.
    Example: If user says "I like coffee", store "I like coffee" NOT "User likes coffee".
    """
)
async def add_memory(content: str, userId: str = DEFAULT_USER_ID) -> str:
    """添加新的记忆到mem0。
    
    这个工具用于存储用户信息、偏好或任何可能在未来对话中有用的相关信息。
    当用户提供关于自己的信息或要求记住某些内容时使用此工具。
    
    参数:
        content: 用户原始的信息
        userId: 用户ID，用于记忆存储。如果未明确提供，则使用默认用户ID
    """
    try:
        # 可以存储为简单语句
        mem0_client.add(content, user_id=userId)
        return f"成功添加记忆: {content}"
    except Exception as e:
        return f"添加记忆时出错: {str(e)}"

@mcp.tool(
    description="""Search through stored memories. This method is called ANYTIME the user asks anything."""
)
async def search_memories(query: str, userId: str = DEFAULT_USER_ID) -> str:
    """搜索存储的记忆。
    
    使用语义搜索来查找与查询相关的记忆。
    每当用户询问任何内容时，都应该调用此方法。
    
    参数:
        query: 搜索查询。这是用户提出的查询。例如："上周我告诉你关于天气的什么？"或"我告诉过你关于我朋友小明的什么？"
        userId: 用户ID，用于记忆存储。如果未明确提供，则使用默认用户ID
    """
    try:
        memories = mem0_client.search(query, user_id=userId, limit=5)
        if not memories or not memories.get("results"):
            return "未找到相关记忆。"
        
        results = []
        for i, result in enumerate(memories["results"], 1):
            memory_content = result.get("memory", "")
            score = result.get("score", 0)
            results.append(f"{i}. {memory_content} (相关度: {score:.4f})")
        
        return "找到以下相关记忆:\n" + "\n".join(results)
    except Exception as e:
        return f"搜索记忆时出错: {str(e)}"

@mcp.tool(
    description="""Get all memories for a specific user. This provides a complete view of all stored information about the user."""
)
async def get_all_memories(userId: str = DEFAULT_USER_ID) -> str:
    """获取特定用户的所有记忆。
    
    返回用户的所有存储记忆，提供完整的用户信息视图。
    
    参数:
        userId: 用户ID，用于记忆存储。如果未明确提供，则使用默认用户ID
    """
    try:
        memories = mem0_client.get_all(user_id=userId, page=1, page_size=50)
        if not memories or not memories.get("results"):
            return "该用户没有存储的记忆。"
        
        results = []
        for i, memory in enumerate(memories["results"], 1):
            memory_content = memory.get("memory", "")
            created_at = memory.get("created_at", "")
            results.append(f"{i}. {memory_content}\n   创建时间: {created_at}")
        
        return f"用户 {userId} 的所有记忆:\n" + "\n".join(results)
    except Exception as e:
        return f"获取记忆时出错: {str(e)}"

@mcp.tool(
    description="""Delete a specific memory by its ID. Use this when information is no longer relevant or needs to be removed."""
)
async def delete_memory(memoryId: str, userId: str = DEFAULT_USER_ID) -> str:
    """删除特定的记忆。
    
    通过记忆ID删除特定的记忆。当信息不再相关或需要被移除时使用此工具。
    
    参数:
        memoryId: 要删除的记忆的ID
        userId: 用户ID，用于记忆存储。如果未明确提供，则使用默认用户ID
    """
    try:
        mem0_client.delete(memory_id=memoryId, user_id=userId)
        return f"成功删除记忆 ID: {memoryId}"
    except Exception as e:
        return f"删除记忆时出错: {str(e)}"

@mcp.tool(
    description="""Update an existing memory with new content. Use this to modify or correct previously stored information."""
)
async def update_memory(memoryId: str, newContent: str, userId: str = DEFAULT_USER_ID) -> str:
    """更新现有记忆的内容。
    
    修改或更正先前存储的信息。
    
    参数:
        memoryId: 要更新的记忆的ID
        newContent: 记忆的新内容
        userId: 用户ID，用于记忆存储。如果未明确提供，则使用默认用户ID
    """
    try:
        mem0_client.update(memory_id=memoryId, content=newContent, user_id=userId)
        return f"成功更新记忆 ID: {memoryId}"
    except Exception as e:
        return f"更新记忆时出错: {str(e)}"

@mcp.tool(
    description="""Add a conversation as memory. This stores an entire conversation thread between the user and assistant."""
)
async def add_conversation_memory(messages: list, userId: str = DEFAULT_USER_ID) -> str:
    """添加对话作为记忆。
    
    存储用户和助手之间的整个对话线程。
    
    参数:
        messages: 对话消息列表，格式为[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        userId: 用户ID，用于记忆存储。如果未明确提供，则使用默认用户ID
    """
    try:
        mem0_client.add(messages, user_id=userId)
        return "成功添加对话记忆"
    except Exception as e:
        return f"添加对话记忆时出错: {str(e)}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建一个可以使用SSE为提供的mcp服务器提供服务的Starlette应用程序。"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='运行基于SSE的MCP记忆服务器')
    parser.add_argument('--host', default='0.0.0.0', help='绑定的主机')
    parser.add_argument('--port', type=int, default=8080, help='监听的端口')
    args = parser.parse_args()

    # 绑定SSE请求处理到MCP服务器
    starlette_app = create_starlette_app(mcp_server, debug=True)

    print(f"启动记忆MCP服务器，监听 {args.host}:{args.port}")
    uvicorn.run(starlette_app, host=args.host, port=args.port)