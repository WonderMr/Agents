# Agents Directory

Contains specialized AI agent personas, each with a unique identity, protocol, and capabilities.

## Structure

```
agents/
├── common/                    # Shared protocols for all agents
│   ├── core-protocol.mdc      # Base protocol (lifecycle, rules)
│   └── response-footer.mdc    # Mandatory footer format
├── universal_agent/           # General-purpose agent
├── software_engineer/         # Code and development
├── security_expert/           # Security analysis
├── ... (other agents)
└── README.md
```

Each agent directory contains:
- `system_prompt.mdc` — YAML frontmatter + Markdown defining the agent

## Frontmatter Schema

```yaml
---
identity:
  name: "agent_name"           # Unique identifier (snake_case)
  display_name: "Agent Name"   # Human-readable name
  role: "Role Description"     # Agent's expertise area
  tone: "Communication style"  # Voice characteristics
routing:
  domain_keywords:             # Keywords for auto-routing
    - "keyword1"
    - "keyword2"
  trigger_command: "/cmd"      # Slash command trigger
context:
  file_globs:                  # Files to auto-include
    - "**/*.py"
static_skills:                 # Skills for static mode
  - "skill-name.mdc"
preferred_skills:              # Skills for RAG selection
  - "skill-name"
---
# Agent Name System Prompt

## Identity
You are a **Role**...

## Protocol
1. Step one
2. Step two

## Output Spec
...
```

## Available Agents

| Agent | Trigger | Domain |
|-------|---------|--------|
| `universal_agent` | `/universal` | General tasks, planning, orchestration |
| `software_engineer` | `/dev` | Code, debugging, architecture |
| `security_expert` | `/security` | Vulnerability analysis, secure code |
| `deep_researcher` | `/research` | Research, 80/20 synthesis |
| `tech_writer` | `/docs` | Documentation, git commits |
| `data_analyst` | `/data` | Data analysis, visualization |
| `bio_hacker` | `/bio` | Biology, health optimization |
| `psychologist` | `/psy` | Emotional support, CBT, NVC |
| `medical_expert` | `/doctor` | Clinical analysis, diagnosis |
| `investigative_analyst` | `/investigate` | OSINT, fact-checking |
| `diagram_architect` | `/draw` | Mermaid diagrams |
| `mcp_builder` | `/mcp` | MCP server development |
| `agent_builder` | `/new_agent` | Creating new agents |
| `purchase_researcher` | `/purchase` | Product research, decision matrices |
| `presentation_coach` | `/presentation` | Slide design, delivery |
| `daily_briefing` | `/briefing` | News digest, strategic analysis |
| `3d_print_finder` | `/3dprint` | 3D model search |
| `instagram_analyst` | `/insta` | Content analysis, viral mechanics |
| `website_analyst` | `/site` | Site audits, business models |
| `document_ocr_expert` | `/ocr` | PDF/image text extraction |
| `semantic_expert` | `/semantic` | Forensic summarization |
| `data_forensic` | `/forensic` | Leak analysis, deduplication |
| `black_hole_finder` | `/blackhole` | Knowledge gap detection |
| `ai_debugger` | `/debug_ai` | AI system debugging |
| `ai_senior_engineer` | `/ai_arch` | HAI design, cognitive ergonomics |
| `alerts_describer` | `/alerts` | Infrastructure alert documentation |

## Common Components

### core-protocol.mdc

Base protocol inherited by all agents:
- **Pre-flight**: MCP check, context loading, header formation
- **Execution**: Apply agent logic and skills
- **Post-flight**: Language check, footer formatting
- **Logging**: Trace to Langfuse

### response-footer.mdc

Mandatory footer format for all responses including:
- Profile identification
- Loaded skills/implants

## Creating a New Agent

1. **Create directory**:
   ```bash
   mkdir -p .cursor/agents/my_agent
   ```

2. **Create system_prompt.mdc**:
   ```yaml
   ---
   identity:
     name: "my_agent"
     display_name: "My Agent"
     role: "Expert in Domain"
     tone: "Professional, Clear"
   routing:
     domain_keywords: ["domain", "topic"]
     trigger_command: "/myagent"
   static_skills:
     - "skill-relevant.mdc"
   preferred_skills:
     - "skill-relevant"
   ---
   # My Agent System Prompt

   ## Identity
   You are an expert in **Domain**...

   ## Protocol
   Apply Global Protocol: `.cursor/agents/common/core-protocol.mdc`

   1. **STEP ONE**
      * Action details

   ## Output Spec
   * Format requirements
   ```

3. **Create rule** in `.cursor/rules/10-my-agent.mdc`

4. **Create command** in `.cursor/commands/myagent.md`

## Agent Selection

Agents are selected via:
1. **Trigger command**: Explicit `/command` invocation
2. **Semantic routing**: `domain_keywords` matching
3. **Cache**: Previous routing decisions cached
4. **Fallback**: `universal_agent` for ambiguous queries
