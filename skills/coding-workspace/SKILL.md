---
name: coding-workspace
description: Use this skill for software development requests that require planning, editing, or generating files inside the workspace directory while following the project's local coding constraints.
metadata:
  owner: devmate
  version: "1.0"
---

# coding-workspace

## Overview

This skill helps the agent complete coding requests safely inside the local workspace.

## Instructions

1. Treat `/workspace/` as the only writable project area unless the user explicitly asks for something else.
2. Start by inspecting the relevant files with the built-in filesystem tools before making edits.
3. Use `search_rag` when the task might depend on internal project rules or local documentation.
4. Use `search_web` when the task depends on current framework, package, or API guidance.
5. Keep changes minimal, coherent, and runnable. Prefer editing existing files over generating unnecessary new files.
6. After writing files, verify that the result matches the user's request and summarize what was created or changed.
