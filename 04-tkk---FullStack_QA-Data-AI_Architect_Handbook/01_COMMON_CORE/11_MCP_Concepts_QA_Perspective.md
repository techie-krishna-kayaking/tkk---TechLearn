# MCP Concepts - Model Context Protocol from QA Perspective

## Executive Summary

Model Context Protocol (MCP) is an open protocol that standardizes how AI applications connect to data sources and tools. Developed by Anthropic, MCP enables LLMs to securely interact with databases, APIs, file systems, and business applications through a unified interface. From a **QA perspective**, testing MCP implementations requires validating server connections, tool/resource exposure, security controls, and integration workflows.

**Target Audience**: Senior QA engineers (8+ years) testing agentic AI systems, LLM tool integrations, and enterprise AI platforms using MCP.

---

## Why This Matters in Enterprise

### Business Impact
- **Standardization**: MCP provides unified protocol for LLM-data integration (like USB for AI applications)
- **Ecosystem growth**: 50+ MCP servers available (databases, APIs, file systems, CRMs)
- **Developer productivity**: 3-5x faster integration vs. custom implementations
- **Enterprise adoption**: Claude Desktop, Zed Editor, Continue.dev support MCP natively

### Technical Imperative
- **Security**: MCP enforces permission models, prevents unauthorized data access
- **Interoperability**: Single MCP client works with any MCP server (vendor-agnostic)
- **Modularity**: Add/remove data sources without changing application code
- **Observability**: Standardized logging, monitoring, debugging across integrations

### Career Value
- **Emerging standard**: MCP expertise differentiator in AI QA market
- **Transferable skills**: Concepts apply to API testing, integration testing, security testing
- **Future-proof**: As MCP adoption grows, expertise becomes more valuable

---

## Scope and Boundaries

### In Scope
- MCP architecture (client-server model, transport layers)
- MCP primitives (resources, tools, prompts, sampling)
- MCP security model (authentication, authorization, sandboxing)
- Testing MCP servers (connection, resource listing, tool execution)
- Testing MCP clients (server discovery, request handling, error management)
- Integration testing (end-to-end workflows)

### Out of Scope
- LLM fundamentals (covered in [08_LLM_Concepts_QA_Perspective.md](./08_LLM_Concepts_QA_Perspective.md))
- Agentic AI architecture (covered in [12_AI_Agentic_Concepts_QA_Perspective.md](./12_AI_Agentic_Concepts_QA_Perspective.md))
- Platform-specific MCP implementations (covered in stack files)

---

## MCP Architecture

### Client-Server Model

    ```mermaid
    graph LR
        A[LLM Application<br/>MCP Client] <-->|MCP Protocol| B[MCP Server 1<br/>Database]
        A <-->|MCP Protocol| C[MCP Server 2<br/>File System]
        A <-->|MCP Protocol| D[MCP Server 3<br/>Slack API]
        
        B --> E[(PostgreSQL)]
        C --> F[(/Documents)]
        D --> G[Slack Workspace]
        
        style A fill:#e1f5ff
        style B fill:#ffe1f5
        style C fill:#ffe1f5
        style D fill:#ffe1f5
    ```

**Key Components**:

1. **MCP Client** (Host Application):
   - Claude Desktop, Zed Editor, custom AI apps
   - Discovers and connects to MCP servers
   - Makes requests for resources, tools, prompts

2. **MCP Server** (Data/Tool Provider):
   - Exposes resources (files, database records)
   - Exposes tools (functions that perform actions)
   - Handles authentication, authorization

3. **Transport Layer**:
   - **Standard I/O (stdio)**: Process spawning (local servers)
   - **Server-Sent Events (SSE)**: HTTP-based (remote servers)

---

## MCP Primitives

### 1. Resources (Read-Only Data)

**Definition**: Contextual data exposed to LLM (files, database records, API responses).

**Example**:
    ```json
    {
      "uri": "file:///path/to/document.txt",
      "name": "Company Policy Document",
      "mimeType": "text/plain",
      "text": "Our vacation policy is..."
    }
    ```

**QA Test**:
    ```python
    import mcp
    
    def test_resource_listing():
        # Connect to MCP server
        client = mcp.ClientSession(server_params={
            "command": "python",
            "args": ["server.py"]
        })
        
        # List available resources
        resources = client.list_resources()
        
        # Validate resources exposed
        assert len(resources) > 0, "No resources exposed by server"
        
        # Validate resource structure
        for resource in resources:
            assert "uri" in resource, f"Resource missing URI: {resource}"
            assert "name" in resource, f"Resource missing name: {resource}"
            assert "mimeType" in resource or "text" in resource, \
                f"Resource missing content: {resource}"
    ```

**Test Resource Access**:
    ```python
    def test_resource_read():
        client = mcp.ClientSession(server_params={...})
        
        # Read specific resource
        resource = client.read_resource("file:///path/to/document.txt")
        
        # Validate content returned
        assert resource["text"] is not None, "Resource content empty"
        assert len(resource["text"]) > 0, "Resource text empty"
        
        # Validate metadata
        assert resource["mimeType"] == "text/plain", \
            f"Unexpected MIME type: {resource['mimeType']}"
    ```

### 2. Tools (Executable Functions)

**Definition**: Functions that LLM can invoke to perform actions.

**Example**:
    ```json
    {
      "name": "query_database",
      "description": "Execute SQL query on database",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "SQL query to execute"
          }
        },
        "required": ["query"]
      }
    }
    ```

**QA Test**:
    ```python
    def test_tool_listing():
        client = mcp.ClientSession(server_params={...})
        
        # List available tools
        tools = client.list_tools()
        
        # Validate tools exposed
        assert len(tools) > 0, "No tools exposed by server"
        
        # Validate tool structure
        for tool in tools:
            assert "name" in tool, f"Tool missing name: {tool}"
            assert "description" in tool, f"Tool missing description: {tool}"
            assert "inputSchema" in tool, f"Tool missing input schema: {tool}"
    ```

**Test Tool Execution**:
    ```python
    def test_tool_execution():
        client = mcp.ClientSession(server_params={...})
        
        # Execute tool
        result = client.call_tool(
            name="query_database",
            arguments={"query": "SELECT COUNT(*) FROM customers"}
        )
        
        # Validate result structure
        assert "content" in result, "Tool result missing content"
        assert len(result["content"]) > 0, "Tool result empty"
        
        # Validate result format
        content = result["content"][0]
        assert content["type"] == "text", f"Unexpected content type: {content['type']}"
        assert "text" in content, "Result missing text field"
    ```

### 3. Prompts (Templated Messages)

**Definition**: Pre-defined prompt templates with variables.

**Example**:
    ```json
    {
      "name": "analyze_data",
      "description": "Analyze dataset with specific focus",
      "arguments": [
        {
          "name": "dataset_name",
          "description": "Name of dataset to analyze",
          "required": true
        },
        {
          "name": "focus_area",
          "description": "Specific area to focus on",
          "required": false
        }
      ]
    }
    ```

**QA Test**:
    ```python
    def test_prompt_listing():
        client = mcp.ClientSession(server_params={...})
        
        # List available prompts
        prompts = client.list_prompts()
        
        # Validate prompts exposed
        assert len(prompts) > 0, "No prompts exposed by server"
        
        # Validate prompt structure
        for prompt in prompts:
            assert "name" in prompt, f"Prompt missing name: {prompt}"
            assert "description" in prompt, f"Prompt missing description: {prompt}"
    ```

**Test Prompt Retrieval**:
    ```python
    def test_prompt_get():
        client = mcp.ClientSession(server_params={...})
        
        # Get prompt with arguments
        prompt = client.get_prompt(
            name="analyze_data",
            arguments={
                "dataset_name": "sales_2024",
                "focus_area": "regional trends"
            }
        )
        
        # Validate prompt content
        assert "messages" in prompt, "Prompt missing messages"
        assert len(prompt["messages"]) > 0, "Prompt messages empty"
        
        # Validate argument substitution
        prompt_text = str(prompt["messages"])
        assert "sales_2024" in prompt_text, "Dataset name not substituted"
        assert "regional trends" in prompt_text, "Focus area not substituted"
    ```

### 4. Sampling (LLM Completion Requests)

**Definition**: MCP server requests LLM completion from client.

**Use Case**: Server needs LLM to process retrieved data before returning to client.

**QA Test**:
    ```python
    def test_sampling_request():
        # Mock client that handles sampling
        class MockClient(mcp.ClientSession):
            def create_message(self, messages, **kwargs):
                # Simulate LLM response
                return {
                    "role": "assistant",
                    "content": "Mocked LLM response"
                }
        
        client = MockClient(server_params={...})
        
        # Server makes sampling request
        result = client.call_tool(
            name="summarize_document",
            arguments={"document_id": "doc123"}
        )
        
        # Validate server used sampling
        assert "Mocked LLM response" in str(result), \
            "Server did not use sampling for summarization"
    ```

---

## MCP Security Model

### 1. Authentication

**Server Authentication** (Client → Server):
    ```python
    def test_server_authentication():
        # Configure client with API key
        client = mcp.ClientSession(
            server_params={
                "command": "python",
                "args": ["server.py"],
                "env": {
                    "API_KEY": "secret_key_12345"
                }
            }
        )
        
        # Server validates API key on connection
        try:
            tools = client.list_tools()
            assert len(tools) > 0, "Authenticated successfully"
        except Exception as e:
            pytest.fail(f"Authentication failed: {e}")
    ```

**Test Invalid Credentials**:
    ```python
    def test_invalid_authentication():
        # Configure client with invalid API key
        client = mcp.ClientSession(
            server_params={
                "command": "python",
                "args": ["server.py"],
                "env": {
                    "API_KEY": "invalid_key"
                }
            }
        )
        
        # Expect authentication failure
        with pytest.raises(Exception, match="authentication"):
            client.list_tools()
    ```

### 2. Authorization (Resource-Level Permissions)

    ```python
    def test_resource_authorization():
        client = mcp.ClientSession(
            server_params={...},
            user_role="analyst"  # Limited permissions
        )
        
        # Analyst can read public documents
        public_resource = client.read_resource("file:///public/report.txt")
        assert public_resource is not None
        
        # Analyst cannot read confidential documents
        with pytest.raises(Exception, match="permission denied"):
            client.read_resource("file:///confidential/salaries.txt")
    ```

### 3. Sandboxing (Tool Execution Limits)

    ```python
    def test_tool_sandboxing():
        client = mcp.ClientSession(server_params={...})
        
        # Safe query (allowed)
        result = client.call_tool(
            name="query_database",
            arguments={"query": "SELECT * FROM customers LIMIT 10"}
        )
        assert result is not None
        
        # Dangerous query (blocked)
        with pytest.raises(Exception, match="not allowed"):
            client.call_tool(
                name="query_database",
                arguments={"query": "DROP TABLE customers"}
            )
    ```

---

## MCP Server Testing

### 1. Connection Testing

**Test stdio Transport**:
    ```python
    def test_stdio_connection():
        import subprocess
        
        # Spawn MCP server process
        process = subprocess.Popen(
            ["python", "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Validate process started
        assert process.poll() is None, "Server process failed to start"
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "1.0.0"}
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline().decode()
        response = json.loads(response_line)
        
        # Validate initialization
        assert "result" in response, f"Initialization failed: {response}"
        assert response["result"]["protocolVersion"] == "1.0.0"
        
        # Cleanup
        process.terminate()
    ```

**Test SSE Transport**:
    ```python
    import requests
    
    def test_sse_connection():
        # Start SSE server
        server_url = "http://localhost:8080/sse"
        
        # Connect to SSE endpoint
        response = requests.get(server_url, stream=True)
        
        # Validate connection
        assert response.status_code == 200, f"SSE connection failed: {response.status_code}"
        assert response.headers["Content-Type"] == "text/event-stream", \
            f"Wrong content type: {response.headers['Content-Type']}"
        
        # Read first event
        for line in response.iter_lines():
            if line.startswith(b"data:"):
                data = json.loads(line[5:])
                assert "method" in data, "Invalid SSE message format"
                break
    ```

### 2. Resource Testing

**Test Resource Discovery**:
    ```python
    def test_resource_discovery():
        client = mcp.ClientSession(server_params={...})
        
        # List resources
        resources = client.list_resources()
        
        # Validate expected resources present
        resource_uris = [r["uri"] for r in resources]
        expected_uris = [
            "file:///docs/policy.txt",
            "db://localhost/customers",
            "api://slack.com/messages"
        ]
        
        for expected_uri in expected_uris:
            assert any(expected_uri in uri for uri in resource_uris), \
                f"Expected resource not found: {expected_uri}"
    ```

**Test Resource Pagination**:
    ```python
    def test_resource_pagination():
        client = mcp.ClientSession(server_params={...})
        
        # Request first page
        page1 = client.list_resources(limit=10)
        assert len(page1) == 10, f"Expected 10 resources, got {len(page1)}"
        
        # Request second page
        if "nextCursor" in page1:
            page2 = client.list_resources(cursor=page1["nextCursor"], limit=10)
            assert len(page2) <= 10, f"Page 2 size exceeds limit: {len(page2)}"
            
            # Validate no duplicates across pages
            page1_uris = {r["uri"] for r in page1}
            page2_uris = {r["uri"] for r in page2}
            assert len(page1_uris & page2_uris) == 0, "Duplicate resources across pages"
    ```

### 3. Tool Testing

**Test Tool Schema Validation**:
    ```python
    from jsonschema import validate, ValidationError
    
    def test_tool_schema():
        client = mcp.ClientSession(server_params={...})
        
        # Get tool definition
        tools = client.list_tools()
        tool = next(t for t in tools if t["name"] == "query_database")
        
        # Validate against MCP tool schema
        tool_schema = {
            "type": "object",
            "required": ["name", "description", "inputSchema"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "inputSchema": {"type": "object"}
            }
        }
        
        try:
            validate(instance=tool, schema=tool_schema)
        except ValidationError as e:
            pytest.fail(f"Tool schema invalid: {e}")
    ```

**Test Tool Input Validation**:
    ```python
    def test_tool_input_validation():
        client = mcp.ClientSession(server_params={...})
        
        # Valid input
        result = client.call_tool(
            name="query_database",
            arguments={"query": "SELECT * FROM users"}
        )
        assert result is not None
        
        # Invalid input (missing required field)
        with pytest.raises(Exception, match="required.*query"):
            client.call_tool(
                name="query_database",
                arguments={}
            )
        
        # Invalid input (wrong type)
        with pytest.raises(Exception, match="type"):
            client.call_tool(
                name="query_database",
                arguments={"query": 123}  # Should be string
            )
    ```

---

## MCP Client Testing

### 1. Server Discovery

    ```python
    def test_client_server_discovery():
        # Configure client with multiple servers
        client = mcp.Client(servers=[
            {"name": "database", "command": "python", "args": ["db_server.py"]},
            {"name": "filesystem", "command": "python", "args": ["fs_server.py"]},
            {"name": "slack", "command": "python", "args": ["slack_server.py"]}
        ])
        
        # Initialize all servers
        client.initialize()
        
        # Validate all servers connected
        connected_servers = client.list_servers()
        assert len(connected_servers) == 3, \
            f"Expected 3 servers, connected to {len(connected_servers)}"
        
        # Validate server names
        server_names = {s["name"] for s in connected_servers}
        assert server_names == {"database", "filesystem", "slack"}
    ```

### 2. Request Routing

    ```python
    def test_client_request_routing():
        client = mcp.Client(servers=[...])
        
        # Request resources from all servers
        all_resources = client.list_resources()
        
        # Validate resources from multiple servers
        sources = {r.get("metadata", {}).get("server") for r in all_resources}
        assert len(sources) > 1, "Client not aggregating from multiple servers"
        
        # Request from specific server
        db_resources = client.list_resources(server="database")
        
        # Validate only database resources returned
        for resource in db_resources:
            assert resource["uri"].startswith("db://"), \
                f"Non-database resource in filtered results: {resource['uri']}"
    ```

### 3. Error Handling

    ```python
    def test_client_error_handling():
        client = mcp.Client(servers=[...])
        
        # Test server crash during request
        with pytest.raises(Exception, match="server.*disconnected"):
            # Simulate server crash
            client._servers["database"].process.kill()
            
            # Attempt request
            client.list_resources(server="database")
        
        # Test invalid server name
        with pytest.raises(Exception, match="unknown server"):
            client.list_resources(server="nonexistent")
    ```

---

## Integration Testing

### End-to-End Workflow

    ```python
    def test_e2e_rag_workflow():
        """Test RAG workflow using MCP"""
        
        # Step 1: Initialize MCP client
        client = mcp.ClientSession(server_params={
            "command": "python",
            "args": ["document_server.py"]
        })
        
        # Step 2: Query for relevant resources
        query = "What is the vacation policy?"
        resources = client.list_resources()
        
        # Filter resources by relevance (simplified)
        relevant_resources = [
            r for r in resources 
            if "vacation" in r["name"].lower() or "policy" in r["name"].lower()
        ]
        
        assert len(relevant_resources) > 0, "No relevant resources found"
        
        # Step 3: Read resource content
        resource_content = client.read_resource(relevant_resources[0]["uri"])
        context = resource_content["text"]
        
        assert "vacation" in context.lower(), "Resource content not relevant"
        
        # Step 4: Use tool to generate answer
        result = client.call_tool(
            name="answer_question",
            arguments={
                "question": query,
                "context": context
            }
        )
        
        # Validate answer
        answer = result["content"][0]["text"]
        assert len(answer) > 0, "Empty answer generated"
        assert "vacation" in answer.lower(), "Answer not relevant to query"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What is MCP and why was it created?  
**A1**: Model Context Protocol = open standard for AI-data integration (like USB for AI). Created by Anthropic to replace fragmented custom integrations. Benefits: Interoperability (one client, many servers), security (standardized auth), modularity (plug-and-play data sources).

**Q2**: What are the main MCP primitives?  
**A2**: (1) **Resources**: Read-only data (files, DB records), (2) **Tools**: Executable functions (query DB, call API), (3) **Prompts**: Template messages with variables, (4) **Sampling**: Server requests LLM completion from client.

### Advanced (4-8 years)
**Q3**: How do you test MCP security?  
**A3**: (1) **Authentication**: Test valid/invalid credentials, (2) **Authorization**: Verify role-based access (analyst can't read admin files), (3) **Sandboxing**: Validate dangerous operations blocked (DROP TABLE rejected), (4) **Input validation**: Test malicious inputs (SQL injection, path traversal), (5) **Audit logging**: Confirm all access logged.

**Q4**: Difference between stdio and SSE transport?  
**A4**: **stdio**: Process spawning, local servers, simpler. **SSE**: HTTP-based, remote servers, scalable. Use stdio for local tools (filesystem), SSE for cloud services (APIs). Test both by validating connection, message exchange, disconnection handling.

### Scenario (8-12 years)
**Q5**: MCP server crashes when querying large database. Troubleshoot?  
**A5**: (1) **Memory**: Check server memory usage (process killed by OOM), (2) **Query timeout**: Add timeout to DB queries (prevent hang), (3) **Result size**: Limit query results (LIMIT 1000), (4) **Pagination**: Implement cursor-based pagination for large result sets, (5) **Streaming**: Stream results instead of buffering all in memory, (6) **Test**: Reproduce with large dataset, validate fixes, load test.

### Architect (12+ years)
**Q6**: Design MCP-based multi-tenant enterprise AI platform?  
**A6**: (1) **Architecture**: Central MCP client (AI app), tenant-specific MCP servers (data silos), (2) **Isolation**: Separate server instance per tenant (no data leakage), (3) **Authentication**: OAuth 2.0 with tenant ID in token, (4) **Authorization**: RBAC (admin/analyst/viewer roles), resource-level ACLs, (5) **Monitoring**: Centralized logging (ELK), per-tenant metrics (Prometheus), (6) **Scaling**: Kubernetes deployment, auto-scale servers based on load, (7) **Testing**: Multi-tenant test suite (validate isolation), load test (1000 concurrent users), security audit (penetration testing), (8) **Compliance**: Audit logs (SOC 2), encryption at rest/transit (GDPR), data residency (region-specific servers).

---

## Frequently Asked Questions

**Q1**: How does MCP compare to function calling?  
**A1**: **MCP**: Standardized protocol, server-side tool definitions, multi-tool orchestration, security built-in. **Function calling**: LLM-native (OpenAI, Anthropic), client-side definitions, single-turn. MCP better for enterprise (governance, reusability), function calling simpler for quick prototypes.

**Q2**: Can MCP servers be chained?  
**A2**: Yes. Server A can act as client to Server B. Example: Orchestrator server coordinates multiple domain-specific servers (DB, API, filesystem). Test by validating request flows through chain.

**Q3**: How to handle MCP server failures?  
**A3**: (1) **Retry**: Exponential backoff (1s, 2s, 4s), (2) **Fallback**: Secondary server if primary fails, (3) **Circuit breaker**: Stop requests after N failures (prevent cascade), (4) **Monitoring**: Alert on high error rate. Test by simulating failures.

**Q4**: How to version MCP servers?  
**A4**: (1) **Protocol version**: MCP supports version negotiation (client/server agree), (2) **Server version**: Include in metadata (v1.2.3), (3) **Deprecation**: Announce removal timeline, maintain backward compatibility, (4) **Testing**: Test new clients with old servers (compatibility).

**Q5**: How to debug MCP requests?  
**A5**: (1) **Logging**: Enable verbose logging in client/server, (2) **Tracing**: Log request ID across client-server boundary, (3) **Inspection**: Use MCP inspector tool (browser-based debugger), (4) **Testing**: Unit test servers independently, integration test with mock client.

**Q6**: Can MCP work with non-LLM applications?  
**A6**: Yes. MCP is protocol-agnostic (not LLM-specific). Can use for any app needing standardized data/tool access. Example: Data pipeline orchestrator using MCP to discover/execute data sources.

**Q7**: How to implement rate limiting in MCP?  
**A7**: (1) **Server-side**: Token bucket (N requests/minute), return 429 error when exceeded, (2) **Client-side**: Respect retry-after header, queue requests, (3) **Testing**: Send burst of requests, validate rate limit enforced, check error messages.

**Q8**: How to handle long-running MCP operations?  
**A8**: (1) **Async execution**: Return task ID immediately, poll for status, (2) **Webhooks**: Server notifies client on completion, (3) **Streaming**: Stream partial results (SSE), (4) **Timeout**: Client timeout (30s), server timeout (5 min). Test with slow operation (simulate delay).

**Q9**: How to test MCP with mock servers?  
**A9**: Create lightweight mock server (returns hardcoded responses), use for client testing (no real DB/API needed). Example: Mock DB server returns canned query results. Validate client handles responses correctly.

**Q10**: What is the MCP registry?  
**A10**: Community directory of MCP servers (like npm for MCP). Discover existing servers (Postgres, Slack, GitHub), reuse instead of building. Test by installing from registry, validating functionality.

**Q11**: How to secure MCP in production?  
**A11**: (1) **TLS**: Encrypt transport (SSE over HTTPS), (2) **Auth**: API keys, OAuth tokens, (3) **Network**: Firewall rules (only allow MCP ports), VPN for remote access, (4) **Least privilege**: Minimal permissions per server, (5) **Audit**: Log all access, monitor for anomalies.

**Q12**: How to test MCP performance?  
**A12**: (1) **Latency**: Measure request-response time (p95 <100ms target), (2) **Throughput**: Requests/sec (target: 1000 req/s), (3) **Concurrency**: 100 concurrent connections, (4) **Resource usage**: Monitor CPU, memory, (5) **Load test**: JMeter, Locust scripts.

**Q13**: Can MCP servers expose real-time data?  
**A13**: Yes. Resources can be dynamic (current stock price, live sensor data). Server refreshes on each request or implements caching. Test by querying multiple times, validating data updates.

**Q14**: How to handle MCP backward compatibility?  
**A14**: (1) **Versioned endpoints**: /v1/resources, /v2/resources, (2) **Deprecation warnings**: Return warning header, (3) **Grace period**: Support old version for 6-12 months, (4) **Testing**: Run tests against all supported versions.

**Q15**: What is the MCP lifecycle?  
**A15**: (1) **Discovery**: Client finds servers (config file), (2) **Initialization**: Handshake, capabilities negotiation, (3) **Operation**: Resources/tools/prompts requests, (4) **Termination**: Graceful shutdown, cleanup. Test each phase independently.

**Q16**: How to implement caching in MCP?  
**A16**: (1) **Client-side**: Cache resources (TTL: 5 min), invalidate on update, (2) **Server-side**: Cache DB queries, API responses, (3) **Headers**: Return cache-control headers (max-age), (4) **Testing**: Validate cache hit/miss, expiration.

**Q17**: How to test MCP with large payloads?  
**A17**: (1) **Large resource**: 10MB text file, validate retrieval, (2) **Large result**: Query returning 100K rows, test pagination, (3) **Streaming**: Test chunked transfer, (4) **Limits**: Validate max payload size enforced (reject >100MB).

**Q18**: What is MCP server composition?  
**A18**: Combine multiple servers into single interface (aggregator pattern). Client sees unified view, aggregator routes to backend servers. Test by validating aggregation logic, fallback on failure.

**Q19**: How to monitor MCP in production?  
**A19**: (1) **Metrics**: Request count, latency, error rate (Prometheus), (2) **Logging**: Structured logs (JSON, ELK), (3) **Tracing**: Distributed tracing (Jaeger), (4) **Alerting**: PagerDuty on high error rate, (5) **Dashboards**: Grafana visualizations.

**Q20**: How does MCP handle schema evolution?  
**A20**: (1) **Add fields**: New optional fields backward compatible, (2) **Remove fields**: Deprecate first, remove later, (3) **Rename fields**: Support both old/new names temporarily, (4) **Testing**: Test new client with old server schema, validate graceful degradation.

---

## Actionable Checklists

### MCP Server Testing Checklist
- [ ] Connection established (stdio or SSE)
- [ ] Initialization handshake successful
- [ ] Protocol version negotiation works
- [ ] Resources listed correctly
- [ ] Resource content readable
- [ ] Tools listed with valid schemas
- [ ] Tool execution works (valid inputs)
- [ ] Tool input validation (reject invalid)
- [ ] Prompts listed correctly
- [ ] Authentication validated (valid/invalid credentials)
- [ ] Authorization tested (role-based access)
- [ ] Error handling (graceful failures)
- [ ] Performance tested (latency, throughput)

### MCP Client Testing Checklist
- [ ] Server discovery works (all servers found)
- [ ] Multi-server initialization
- [ ] Request routing (correct server selected)
- [ ] Resource aggregation (from multiple servers)
- [ ] Tool execution across servers
- [ ] Error handling (server crash, network failure)
- [ ] Retry logic (exponential backoff)
- [ ] Timeout handling (request timeout)
- [ ] Logging enabled (request/response traced)
- [ ] Connection pooling (reuse connections)

### MCP Security Testing Checklist
- [ ] Authentication required (no anonymous access)
- [ ] Invalid credentials rejected
- [ ] Authorization enforced (role-based)
- [ ] Sandboxing validated (dangerous ops blocked)
- [ ] Input validation (SQL injection, XSS)
- [ ] TLS/HTTPS enabled (encrypted transport)
- [ ] API keys rotated (not hardcoded)
- [ ] Audit logging enabled (all access logged)
- [ ] Rate limiting enforced (prevent abuse)
- [ ] Penetration testing conducted

---

## References

### Official Documentation
- **MCP Specification**: https://spec.modelcontextprotocol.io
- **MCP SDK (Python)**: https://github.com/modelcontextprotocol/python-sdk
- **MCP SDK (TypeScript)**: https://github.com/modelcontextprotocol/typescript-sdk

### Tutorials
- **Building MCP Servers**: https://modelcontextprotocol.io/tutorials/building-servers
- **MCP Quickstart**: https://modelcontextprotocol.io/quickstart

### Community
- **MCP Registry**: https://github.com/modelcontextprotocol/servers (Community servers)
- **MCP Discord**: Official community for Q&A, discussions

### Tools
- **MCP Inspector**: Browser-based debugging tool
- **Claude Desktop**: Native MCP client
- **Zed Editor**: Code editor with MCP support

---

**Core References**: Platform-agnostic MCP concepts  
**Stack Deltas**: MCP server implementations for specific platforms (Postgres, Slack, AWS) in stack files

**Previous**: [10_RAG_Concepts_QA_Perspective.md](./10_RAG_Concepts_QA_Perspective.md)  
**Next**: [12_AI_Agentic_Concepts_QA_Perspective.md](./12_AI_Agentic_Concepts_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)