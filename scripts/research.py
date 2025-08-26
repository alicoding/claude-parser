#!/usr/bin/env python3
"""
Perplexity Research Tool - 95/5 Architecture
Uses httpx SYNCHRONOUS client (no async needed)
Supports conversation threads and file context
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
import pendulum
from rich.console import Console
from rich.panel import Panel
import orjson
import typer

# Load .env file first
from dotenv import load_dotenv
load_dotenv()

# 95/5 principle: Use high-level libraries
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

# Create typer app
app = typer.Typer(
    help="Research tool for finding high-level libraries",
    epilog="""
Examples:
  # Simple query
  python scripts/research.py "how to parse JSON functionally"
  
  # With model selection
  python scripts/research.py "async alternatives" --model o3-mini-online
  
  # With file context (single)
  python scripts/research.py "fix this error" --file error.log
  
  # With multiple context files
  python scripts/research.py "review this" -c file1.py -c file2.md -c README.md
  
  # Continue previous thread
  python scripts/research.py "what about performance?" --thread 20250821_180000

Model Selection Guide:
  • sonar-pro / o3-mini-online: Best for online research & finding libraries
  • o3-mini: Good for reasoning and logic problems  
  • grok4 / gemini-pro-2.5 / opus-4.1: Complex planning & architecture
  • gemini-flash-2.5: Quick summaries and writing tasks
    """
)


class PerplexityResearcher:
    """Perplexity API wrapper with conversation threads and file context."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "sonar-pro",
        thread_id: Optional[str] = None
    ):
        # Setup
        self.api_key = api_key or os.getenv("ELECTRONHUB_API_KEY")
        self.base_url = os.getenv("ELECTRONHUB_BASE_URL", "https://api.electronhub.ai/v1")
        self.console = Console()
        self.model = model
        
        # Thread management
        self.threads_dir = Path(".claude/research_threads")
        self.threads_dir.mkdir(parents=True, exist_ok=True)
        
        # Use provided thread_id or generate one
        if thread_id:
            self.thread_id = thread_id
        else:
            # Generate thread ID from timestamp
            self.thread_id = pendulum.now().format('YYYYMMDD_HHmmss')
        
        self.thread_file = self.threads_dir / f"{self.thread_id}.json"
        
        # Load existing conversation or start new
        self.messages = self._load_thread()
        
        # Docs directory
        self.docs_dir = Path("docs/research")
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Session file
        self.log_file = self.docs_dir / f"research_{self.thread_id}.md"
        
        # httpx SYNCHRONOUS client (no async needed!)
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        
        # System prompt - enforces high-level library research
        self.system_prompt = """You are a research assistant for a codebase with STRICT quality standards.

🚨 MANDATORY: ALL SOLUTIONS MUST FOLLOW docs/LIBRARY_FIRST_RULE.md
- LIBRARY FIRST OR DIE: 95% library code, 5% glue
- Every line of custom code is a failure to find the right library
- Real failures: 634 lines for 25-line TTL problem, 2,553 lines for 200-line memory project

CRITICAL: You MUST ask for full context before providing answers
- If the user's query lacks specific details, ASK for more information
- If you're unsure about the exact problem, ASK for clarification
- If file paths or error messages would help, REQUEST them
- NEVER hallucinate or guess - always work with concrete information

MANDATORY WORKFLOW (per LIBRARY_FIRST_RULE.md):
1. Task: "Build X functionality"
2. STOP: "What library does X?"
3. Search: Find the highest-level library that does X
4. Found? Recommend it with examples. END.
5. Not found? Provide evidence (PyPI, GitHub, Stack Overflow links)

FORBIDDEN (violations = instant failure per LIBRARY_FIRST_RULE.md):
- json (must use orjson)
- datetime (must use pendulum)
- requests/urllib (must use httpx)
- logging (must use loguru)
- argparse (must use typer/click)
- while True loops (must use apscheduler)
- Manual retry logic (must use tenacity)
- Manual batch processing (must use more-itertools)
- Any manual async/await/threading code
- Any library requiring manual resource management

APPROVED LIBRARIES (use these first):
- Scheduling: apscheduler (NOT while True)
- Events: blinker (NOT if/elif chains)
- Retry: tenacity (NOT try/except loops)
- Batch: more-itertools (NOT manual chunking)
- Dates: pendulum (NOT datetime parsing)
- Async Tasks: arq, celery (NOT asyncio.create_task)
- CLI: typer (NOT argparse)
- Validation: pydantic (NOT manual checks)
- HTTP: httpx (NOT urllib)
- Testing: pytest (NOT unittest)

When researching:
- Find the HIGHEST-LEVEL library that solves the problem
- Prefer libraries that handle complexity internally
- Look for declarative/functional approaches over imperative
- Choose libraries with simple APIs (1-3 function calls for 95% of use cases)

Success metrics:
✅ Success: 95% library code, 5% glue
❌ Failure: 95% custom code, 5% libraries

REMEMBER: Someone already solved your problem - FIND THEIR LIBRARY."""
    
    def _load_thread(self) -> List[Dict]:
        """Load existing conversation thread or start new."""
        if self.thread_file.exists():
            try:
                content = self.thread_file.read_text()
                data = orjson.loads(content)
                self.console.print(f"[green]📎 Resumed thread: {self.thread_id}[/green]")
                self.console.print(f"[dim]💡 TIP: Multi-turn conversations provide better context and results![/dim]")
                self.console.print(f"[dim]   Thread has {len(data.get('messages', []))} previous messages[/dim]")
                return data.get("messages", [])
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load thread: {e}[/yellow]")
                return []
        else:
            self.console.print(f"[cyan]🆕 New thread: {self.thread_id}[/cyan]")
            self.console.print(f"[dim]💡 TIP: Resume this thread for follow-up questions:[/dim]")
            self.console.print(f"[yellow]   python scripts/research.py \"follow-up question\" --thread {self.thread_id}[/yellow]")
            return []
    
    def _save_thread(self):
        """Save conversation thread to disk."""
        data = {
            "thread_id": self.thread_id,
            "model": self.model,
            "created": pendulum.now().isoformat(),
            "messages": self.messages
        }
        self.thread_file.write_text(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode())
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_api_streaming(self, messages: List[Dict]):
        """Call API with streaming - httpx handles it simply."""
        with self.client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": self.model,  # Use the selected model
                "messages": messages,
                "temperature": 0.1,
                "stream": True,
                "citations": True
            }
        ) as response:
            response.raise_for_status()
            # Yield lines as they come
            for line in response.iter_lines():
                yield line
    
    def research(self, query: str, file_path: Optional[str] = None, context_files: Optional[List[str]] = None) -> str:
        """Research with streaming output, file context, and auto-save."""
        # Add file context if provided
        if file_path:
            file_path = Path(file_path)
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    # Add file content to query
                    query = f"""Query: {query}

File Context ({file_path.name}):
```
{content[:10000]}  # Limit to 10k chars
```

Please analyze this file content to answer my query."""
                    self.console.print(f"[dim]📄 Added file context: {file_path}[/dim]")
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not read file: {e}[/yellow]")
            else:
                self.console.print(f"[yellow]Warning: File not found: {file_path}[/yellow]")
        
        # Add multiple context files if provided
        if context_files:
            additional_context = []
            for ctx_path in context_files:
                ctx_path = Path(ctx_path)
                if ctx_path.exists():
                    try:
                        content = ctx_path.read_text()
                        additional_context.append(f"\nFile Context ({ctx_path.name}):\n```\n{content[:10000]}\n```")
                        self.console.print(f"[dim]📄 Added context: {ctx_path}[/dim]")
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not read {ctx_path}: {e}[/yellow]")
                else:
                    self.console.print(f"[yellow]Warning: File not found: {ctx_path}[/yellow]")
            
            if additional_context:
                query = query + "\n" + "\n".join(additional_context) + "\n\nPlease analyze these files to answer my query."
        
        # Display query
        self.console.print(Panel(f"[bold cyan]🔍 Research Query:[/bold cyan]\n{query}", expand=False))
        
        # Add to conversation
        if not self.messages or not any(msg.get("role") == "system" for msg in self.messages):
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": query})
        
        # Stream response
        full_response = ""
        self.console.print("\n[bold green]Research Results:[/bold green]")
        
        try:
            # Process streaming response
            for line in self._call_api_streaming(self.messages):
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    try:
                        data = orjson.loads(chunk)
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                if content:  # Only process non-None content
                                    full_response += content
                                    self.console.print(content, end="")
                    except orjson.JSONDecodeError:
                        continue
            
            # Add assistant response to history
            self.messages.append({"role": "assistant", "content": full_response})
            
            # Save thread and research
            self._save_thread()
            self._save_to_file(query, full_response)
            
            # Display save location
            self.console.print(f"\n[dim]📁 Research saved to: {self.log_file}[/dim]")
            self.console.print(f"[green]🧵 Thread ID: {self.thread_id}[/green]")
            self.console.print(f"[yellow]💡 Continue this conversation:[/yellow]")
            self.console.print(f"   [cyan]python scripts/research.py \"your follow-up\" --thread {self.thread_id}[/cyan]")
            
            return full_response
            
        except httpx.HTTPError as e:
            self.console.print(f"[red]API Error: {e}[/red]")
            return f"Error: {e}"
    
    def _save_to_file(self, query: str, response: str):
        """Save research to markdown file."""
        timestamp = pendulum.now().format('YYYY-MM-DD HH:mm:ss')
        
        # Append to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## Research Query - {timestamp}\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Response:**\n\n{response}\n\n")
            f.write("---\n")
    
    def interactive(self):
        """Interactive research mode - simple loop."""
        self.console.print(Panel(
            f"[bold cyan]🔬 Research Mode[/bold cyan]\n\n"
            f"Thread ID: {self.thread_id}\n"
            f"Model: {self.model}\n\n"
            "Enter queries to research libraries and solutions.\n"
            "Type 'exit' or 'quit' to leave.\n"
            "Type 'file: <path>' to add file context.",
            expand=False
        ))
        
        current_file = None
        
        while True:
            try:
                query = input("\n[Research Query]> ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                
                # Check for file command
                if query.lower().startswith("file:"):
                    file_path = query[5:].strip()
                    if Path(file_path).exists():
                        current_file = file_path
                        self.console.print(f"[green]✓ File context set: {current_file}[/green]")
                    else:
                        self.console.print(f"[red]✗ File not found: {file_path}[/red]")
                    continue
                    
                if query:
                    self.research(query, file_path=current_file)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        # Cleanup
        self.client.close()
        self.console.print("\n[yellow]Research session ended.[/yellow]")
        self.console.print(f"[dim]Thread saved: {self.thread_id}[/dim]")


@app.command()
def main(
    query: Optional[List[str]] = typer.Argument(None, help="Research query"),
    model: str = typer.Option("sonar-pro", "--model", "-m", help="Model: sonar-pro/o3-mini-online (research), o3-mini (reasoning), grok4/gemini-pro-2.5/opus-4.1 (complex)"),
    thread: Optional[str] = typer.Option(None, "--thread", "-t", help="Thread ID for conversation continuity"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="File path to include as context"),
    context: Optional[List[str]] = typer.Option(None, "--context", "-c", help="Multiple files for context (repeat: -c file1.py -c file2.md)")
):
    """Research tool for finding high-level libraries."""
    # Initialize researcher
    researcher = PerplexityResearcher(
        model=model,
        thread_id=thread
    )
    
    try:
        if query:
            # Single query mode
            query_str = " ".join(query)
            researcher.research(query_str, file_path=file, context_files=context)
            researcher.client.close()
        else:
            # Interactive mode
            researcher.interactive()
    except KeyboardInterrupt:
        print("\n[Interrupted]")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        researcher.client.close()


if __name__ == "__main__":
    app()
