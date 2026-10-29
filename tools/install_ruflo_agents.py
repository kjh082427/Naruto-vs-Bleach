"""Install a curated set of ruflo agent definitions into this project's .claude/agents/ruflo/.

Source: tools/ruflo-src (ruvnet/ruflo main, fetched via codeload). Transformations:
- drop the ruflo-specific `hooks:` frontmatter block (shell scripts running unpinned `npx claude-flow@alpha`;
  not Claude Code's hook schema)
- rename legacy MCP tool prefix mcp__claude-flow__ -> mcp__ruflo__ (our MCP server is registered as `ruflo`)
- append a note mapping the legacy memory_usage tool to the current ruflo memory tools

usage: python3 -I tools/install_ruflo_agents.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'ruflo-src', '.claude', 'agents')
DST = os.path.join(ROOT, '.claude', 'agents', 'ruflo')

AGENTS = [
    'core/coder.md', 'core/planner.md', 'core/researcher.md', 'core/reviewer.md', 'core/tester.md',
    'python-specialist.md', 'analysis/code-review/analyze-code-quality.md',
    'swarm/hierarchical-coordinator.md', 'testing/validation/production-validator.md',
]

NOTE = """

## Ruflo tools in this project

The ruflo MCP server is registered as `ruflo` (tools are `mcp__ruflo__*`). The legacy
`memory_usage` tool referenced above maps to `mcp__ruflo__memory_store`,
`mcp__ruflo__memory_retrieve` and `mcp__ruflo__memory_search`. These tools are optional
coordination aids; skip them if they are unavailable.
"""


def strip_hooks(frontmatter):
    out, skipping = [], False
    for line in frontmatter.split('\n'):
        if re.match(r'^hooks:', line):
            skipping = True
            continue
        if skipping and (line.startswith((' ', '\t')) or line == ''):
            continue
        skipping = False
        out.append(line)
    return '\n'.join(out)


def main():
    os.makedirs(DST, exist_ok=True)
    for rel in AGENTS:
        text = open(os.path.join(SRC, rel), encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n', text, re.S)
        front, body = m.group(1), text[m.end():]
        front = strip_hooks(front)
        body = body.replace('mcp__claude-flow__', 'mcp__ruflo__').rstrip() + NOTE
        name = re.search(r'^name:\s*"?([^"\n]+)"?', front, re.M).group(1).strip()
        open(os.path.join(DST, f'{name}.md'), 'w', encoding='utf-8').write(f'---\n{front}\n---\n{body}')
        print('installed', name)


if __name__ == '__main__':
    main()
