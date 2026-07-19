"""
Hackathon Demo: Agentic RAG for DevPulse
Shows off all new features in 5 minutes
"""

import json
from agentic_rag_hackathon import (
    create_agentic_context,
    QuickMemory,
    QuickReACT,
    QuickVectorStore
)

print("\n" + "="*70)
print("🚀 DEVPULSE AGENTIC RAG DEMO")
print("="*70)

# ============================================================================
# 1. MEMORY DEMO
# ============================================================================
print("\n\n📚 MEMORY SYSTEM DEMO")
print("-" * 70)

memory = QuickMemory()

# Remember first query
print("Query 1: 'Which API topics are trending?'")
memory.remember_query(
    query="Which API topics are trending?",
    result={"insights": ["API Design up 20%", "REST APIs stable", "gRPC emerging"]},
    agent="AnalyzerAgent"
)
memory.store_insight("trends", "API Design up 20%")
memory.store_insight("trends", "REST APIs stable")
print("✅ Stored in memory\n")

# Remember second query (different topic)
print("Query 2: 'What about WebAssembly?'")
memory.remember_query(
    query="What about WebAssembly?",
    result={"score": 65, "confidence": "high"},
    agent="PredictorAgent"
)
memory.store_insight("webassembly", "WASM trending in 2024")
print("✅ Stored in memory\n")

# Recall context
print("Query 3: 'Compare trends'")
print("\n📖 Agent recalls context:")
print(memory.get_context())
print(f"\n🧠 Agent remembers {len(memory.history)} past queries")
print(f"📌 Stored {len(memory.insights)} insight topics")

# ============================================================================
# 2. VECTOR STORE DEMO  
# ============================================================================
print("\n\n🔍 VECTOR STORE (Semantic Search) DEMO")
print("-" * 70)

vector_store = QuickVectorStore()

# Add some content
contents = [
    ("api_auth", "Building API authentication with OAuth2 and JWT tokens"),
    ("api_design", "RESTful API design principles and best practices"),
    ("api_performance", "Optimizing API performance with caching strategies"),
    ("wasm", "WebAssembly for high-performance browser applications"),
    ("database", "Database optimization for microservices architecture"),
]

print(f"\nAdding {len(contents)} documents to vector store...")
for id_, content in contents:
    vector_store.add(id_, content)
    print(f"  ✅ {id_}")

# Search
print("\n\n🔎 Search Query: 'API security and authentication'")
results = vector_store.search("API security and authentication", k=3)

for i, result in enumerate(results, 1):
    similarity = result["score"]
    emoji = "⭐" * int(similarity * 5)
    print(f"\n  {i}. [{result['id']}] {emoji} ({similarity:.1%})")
    print(f"     {result['content'][:60]}...")

# ============================================================================
# 3. REACT PLANNER DEMO
# ============================================================================
print("\n\n💭 REACT PLANNER (Reasoning) DEMO")
print("-" * 70)

context = create_agentic_context()
react = context["react"]

print("\nQuery: 'What are the gaps in our mobile content?'\n")
print("Agent thinks and acts...\n")

thinking = react.think_and_act("What are the gaps in our mobile content?", "AnalyzerAgent")

for thought in thinking["thoughts"]:
    print(f"  {thought}")

print(f"\n📝 Context from memory:")
print(f"  {thinking['context']}")

# ============================================================================
# 4. FULL INTEGRATION DEMO
# ============================================================================
print("\n\n🎯 FULL AGENTIC SYSTEM DEMO")
print("-" * 70)

agentic = create_agentic_context()

print("\n1️⃣  User Query: 'Score this draft: Mobile SDK tutorial'")

# Tool call 1: Get context
print("\n   Agent retrieves context from memory...")
context_result = agentic["tools"].call("recall_insights", topic="analysis")
print(f"   ✅ Found {len(context_result['result'])} past insights\n")

# Tool call 2: Search vector store
print("   Agent searches for similar content...")
similar = agentic["tools"].call(
    "search_vector",
    query="mobile SDK tutorial"
)
print(f"   ✅ Found similar content: {similar}\n")

# Store result
print("   Agent stores this interaction...")
agentic["memory"].remember_query(
    query="Score this draft: Mobile SDK tutorial",
    result={"score": 78, "confidence": "high"},
    agent="PredictorAgent"
)
print("   ✅ Stored in memory\n")

# 2️⃣  Follow-up query
print("2️⃣  Follow-up Query: 'Compare this to my last mobile draft'")

print("\n   Agent recalls conversation...")
recent = agentic["memory"].history[-2:]
print(f"   ✅ Remembers {len(recent)} recent queries")
print(f"   📋 Last query: '{recent[0]['query']}' (score: {recent[0]['result']['score']})")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\n" + "="*70)
print("✨ SUMMARY: What Agentic RAG Enables")
print("="*70)

summary = """
✅ MEMORY SYSTEM
   - Agent remembers your questions
   - Can recall context and insights
   - Learns over time
   - Reuses past results

✅ VECTOR SEARCH
   - Finds semantically similar content
   - No exact matching needed
   - Fast retrieval
   - Better recommendations

✅ REACT REASONING
   - Agent explains its thinking
   - Shows all steps (THOUGHT → ACTION → OBSERVATION)
   - Transparent decision-making
   - Builds trust

✅ TOOL INTEGRATION
   - Memory recall
   - Vector search
   - Context retrieval
   - Extensible for more tools

✅ CONVERSATIONAL
   - Multi-turn support
   - Context awareness
   - Smart follow-ups
   - Natural continuity
"""

print(summary)

print("="*70)
print("🎉 Ready for hackathon! Deploy with: orchestrator.run_pipeline()")
print("="*70 + "\n")
