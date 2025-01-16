FROM langchain/langgraph-api:3.11

ADD . /deps/executive-ai-assistant

# Create the secrets directory with proper permissions
RUN mkdir -p /deps/executive-ai-assistant/eaia/.secrets && \
    chmod 755 /deps/executive-ai-assistant/eaia/.secrets

# Install dependencies
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -e /deps/*

# Add a script to generate the secret files at runtime
COPY scripts/generate_secrets.py /deps/executive-ai-assistant/scripts/
RUN chmod 755 /deps/executive-ai-assistant/scripts/generate_secrets.py

# Environment variables
ENV LANGGRAPH_STORE='{"index": {"embed": "openai:text-embedding-3-small", "dims": 1536}}'
ENV LANGSERVE_GRAPHS='{"main": "/deps/executive-ai-assistant/eaia/main/graph.py:graph", "cron": "/deps/executive-ai-assistant/eaia/cron_graph.py:graph", "general_reflection_graph": "/deps/executive-ai-assistant/eaia/reflection_graphs.py:general_reflection_graph", "multi_reflection_graph": "/deps/executive-ai-assistant/eaia/reflection_graphs.py:multi_reflection_graph"}'

WORKDIR /deps/executive-ai-assistant

# Add an entrypoint script to generate secrets before starting the app
COPY docker-entrypoint.sh /
RUN chmod 755 /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Add a default CMD in case none is provided
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]