# Changelog

## Unreleased - Interview Readiness Update

This update aligns DevMate with the interview requirements for a modern
Deep Agents and LangChain based coding agent.

### Changed

- Replaced the previous REST-style `/mcp/search` implementation with a real
  MCP server using Streamable HTTP transport.
- Changed the Agent-side web search integration from direct `requests.post`
  calls to `langchain-mcp-adapters` `MultiServerMCPClient`.
- Kept the primary Agent runtime on `deepagents.create_deep_agent`, with
  `deepagents==0.5.3` and `langchain==1.2.15`.
- Changed the default Skills directory from `./skills` to `.skills` to match
  the assignment requirement.
- Changed generated Skill persistence from custom JSON files to
  `skills/<skill-name>/SKILL.md` format.
- Updated Docker Compose so the Agent container connects to the MCP server at
  `http://mcp:8001/mcp`.
- Updated README startup instructions for the MCP server entry point.

### Added

- Added MCP protocol dependencies:
  - `mcp`
  - `langchain-mcp-adapters`
- Added built-in Deep Agents style skills:
  - `.skills/internal-docs/SKILL.md`
  - `.skills/coding-workspace/SKILL.md`
- Added configurable MCP server fields in `config.toml`:
  - `server_url`
  - `host`
  - `port`
  - `path`

### Removed

- Removed the direct REST client dependency from the Agent web search path.
- Removed reliance on custom JSON Skill files as the primary Skill format.

### Verified

- `uv run python -m compileall src main.py` passes.
- Cursor lints reported no errors on the edited files.
- MCP Streamable HTTP tool discovery was tested with
  `MultiServerMCPClient` and returned `search_web`.
