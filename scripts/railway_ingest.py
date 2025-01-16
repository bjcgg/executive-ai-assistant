#!/usr/bin/env python
import asyncio
from eaia.gmail import fetch_group_emails
from eaia.main.config import get_config
from langgraph_sdk import get_client
import httpx
import uuid
import hashlib
import os


async def main():
    email_address = get_config({"configurable": {}})["email"]
    client = get_client(url=os.environ.get("LANGGRAPH_URL", "http://127.0.0.1:2024"))

    # Fetch emails from last 15 minutes (with some overlap to ensure we don't miss any)
    for email in fetch_group_emails(
        email_address,
        minutes_since=15,  # Slightly longer than cron interval to ensure overlap
    ):
        thread_id = str(
            uuid.UUID(hex=hashlib.md5(email["thread_id"].encode("UTF-8")).hexdigest())
        )
        try:
            thread_info = await client.threads.get(thread_id)
        except httpx.HTTPStatusError as e:
            if "user_respond" in email:
                continue
            if e.response.status_code == 404:
                thread_info = await client.threads.create(thread_id=thread_id)
            else:
                raise e
        
        if "user_respond" in email:
            await client.threads.update_state(thread_id, None, as_node="__end__")
            continue
            
        recent_email = thread_info["metadata"].get("email_id")
        if recent_email == email["id"]:
            continue

        await client.threads.update(thread_id, metadata={"email_id": email["id"]})
        await client.runs.create(
            thread_id,
            "main",
            input={"email": email},
            multitask_strategy="rollback",
        )


if __name__ == "__main__":
    asyncio.run(main()) 