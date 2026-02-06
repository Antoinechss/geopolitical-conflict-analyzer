import os
import asyncio
from typing import Optional


class OllamaClient:
    """
    Async wrapper around `ollama run <model>`.
    Central place for retries/timeouts later.
    """

    def __init__(self, model: Optional[str] = None, timeout_s: int = 60):
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral:instruct")
        self.timeout_s = timeout_s

    async def run(self, prompt: str) -> str:
        prompt = (prompt or "").strip()
        if not prompt:
            return ""

        proc = await asyncio.create_subprocess_exec(
            "ollama",
            "run",
            self.model,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=prompt.encode("utf-8")),
                timeout=self.timeout_s,
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError("LLM timeout")

        if proc.returncode != 0:
            raise RuntimeError((stderr or b"").decode("utf-8", errors="ignore").strip())

        return (stdout or b"").decode("utf-8", errors="ignore").strip()
