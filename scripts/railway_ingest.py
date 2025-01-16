#!/usr/bin/env python
import asyncio
from eaia.gmail import fetch_group_emails
from eaia.main.config import get_config
from langgraph_sdk import get_client
import httpx
import uuid
import hashlib
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Validate LANGGRAPH_URL
    langgraph_url = os.environ.get("LANGGRAPH_URL")
    if not langgraph_url:
        logger.error("LANGGRAPH_URL environment variable is not set")
        sys.exit(1)
    
    logger.info(f"Using LANGGRAPH_URL: {langgraph_url}")
    
    try:
        email_address = get_config({"configurable": {}})["email"]
        client = get_client(url=langgraph_url)
        
        # Test connection to LANGGRAPH_URL
        try:
            # Simple health check
            await client.http.get("/health")
            logger.info("Successfully connected to LANGGRAPH service")
        except httpx.ConnectError:
            logger.error(f"Could not connect to LANGGRAPH service at {langgraph_url}. Please check if the service is running and the URL is correct.")
            sys.exit(1)
        except Exception as e:
            logger.warning(f"Health check failed, but continuing: {str(e)}")

        # Fetch emails from last 15 minutes
        logger.info("Starting email fetch")
        emails = list(fetch_group_emails(
            email_address,
            minutes_since=15,
        ))
        logger.info(f"Found {len(emails)} emails to process")

        # Process each email
        for email in emails:
            try:
                thread_id = str(
                    uuid.UUID(hex=hashlib.md5(email["thread_id"].encode("UTF-8")).hexdigest())
                )
                logger.info(f"Processing email with thread ID: {thread_id}")

                try:
                    thread_info = await client.threads.get(thread_id)
                except httpx.HTTPStatusError as e:
                    if "user_respond" in email:
                        logger.info(f"Skipping user response email in thread: {thread_id}")
                        continue
                    if e.response.status_code == 404:
                        thread_info = await client.threads.create(thread_id=thread_id)
                        logger.info(f"Created new thread: {thread_id}")
                    else:
                        raise e
                
                if "user_respond" in email:
                    await client.threads.update_state(thread_id, None, as_node="__end__")
                    logger.info(f"Updated thread state to __end__: {thread_id}")
                    continue
                    
                recent_email = thread_info["metadata"].get("email_id")
                if recent_email == email["id"]:
                    logger.info(f"Skipping already processed email: {email['id']}")
                    continue

                await client.threads.update(thread_id, metadata={"email_id": email["id"]})
                await client.runs.create(
                    thread_id,
                    "main",
                    input={"email": email},
                    multitask_strategy="rollback",
                )
                logger.info(f"Successfully processed email: {email['id']}")

            except Exception as e:
                logger.error(f"Error processing email: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 