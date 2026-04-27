---
name: internal-docs
description: Use this skill when the user asks about project architecture, internal standards, product knowledge, or local documentation that should be answered from the repository before relying on general web knowledge.
metadata:
  owner: devmate
  version: "1.0"
---

# internal-docs

## Overview

This skill helps the agent answer questions from local documentation and repository context.

## Instructions

1. Use `search_rag` for semantic lookup across local docs.
2. If the retrieved context is incomplete, inspect specific files with the built-in filesystem tools.
3. Prefer local repository facts over generic model knowledge.
4. Only use the MCP-backed `search_web` tool when the user explicitly asks for current external information or when the answer depends on fast-changing package behavior.
