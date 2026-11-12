import re
from typing import List, Dict, Any
from app.rag.retriever import HybridRetriever
from app.rag.vector_store import VectorStore
from app.agents.llm_provider import LLMProvider
from app.models.chat import ChatQuery, ChatResponse, Citation


class ProjectIntelligenceAssistant:
    """
    RAG-grounded Conversational Project Assistant.
    Answers natural language queries strictly grounded in uploaded project artifacts,
    providing citations and document source references.
    """

    def __init__(self, vector_store: VectorStore, retriever: HybridRetriever, llm: LLMProvider):
        self.vector_store = vector_store
        self.retriever = retriever
        self.llm = llm

    def answer_query(self, query_req: ChatQuery) -> ChatResponse:
        query = query_req.query.strip()
        if not query:
            return ChatResponse(
                query="",
                answer="Please enter a valid question regarding the project.",
                citations=[],
                confidence_score=0.0,
                suggested_followups=[],
            )

        if len(self.vector_store.chunks) == 0:
            return ChatResponse(
                query=query,
                answer="No project documents have been ingested yet. Please upload project documents (PDF, DOCX, CSV, TXT) to build the knowledge base before querying.",
                citations=[],
                confidence_score=0.0,
                suggested_followups=[
                    "Upload project proposal or SRS",
                    "Upload sprint meeting notes",
                    "Upload task backlog CSV",
                ],
            )

        # Retrieve relevant grounded chunks
        retrieval_results = self.retriever.retrieve(query, top_k=query_req.top_k or 5)
        citations = [item[2] for item in retrieval_results]

        context_blocks = []
        for chunk, score, citation in retrieval_results:
            context_blocks.append(
                f"[Source: {citation.document_name} | Chunk #{chunk.chunk_index}]:\n{chunk.content}"
            )
        context_str = "\n\n".join(context_blocks)

        prompt = f"""
You are the AI Project Intelligence & Risk Advisor Assistant.
Answer the user's question accurately, truthfully, and strictly based on the provided project document context.
If the information is not present in the context, clearly state that the uploaded documents do not contain this information.
Do not hallucinate facts. Reference the source files where appropriate.

Document Context:
{context_str}

User Question:
{query}
"""
        system_instruction = (
            "You are a helpful, professional project intelligence assistant. "
            "Always cite facts from the uploaded artifacts."
        )

        llm_answer = self.llm.generate_text(prompt, system_instruction=system_instruction)

        if not llm_answer.strip():
            # Heuristic grounded response generator
            llm_answer = self._generate_grounded_heuristic_response(query, retrieval_results)

        # Confidence calculation based on top retrieval score
        top_score = citations[0].score if citations else 0.0
        confidence = min(0.98, max(0.40, top_score))

        # Dynamic suggested followups
        followups = self._generate_suggested_followups(query, citations)

        return ChatResponse(
            query=query,
            answer=llm_answer.strip(),
            citations=citations,
            confidence_score=round(confidence, 2),
            suggested_followups=followups,
        )

    def _generate_grounded_heuristic_response(self, query: str, retrieval_results) -> str:
        if not retrieval_results:
            return "I could not find relevant information in the uploaded project documents to answer your question."

        top_chunk, score, citation = retrieval_results[0]
        query_lower = query.lower()

        # Identify key sentences matching query words
        query_words = set(re.findall(r"\w+", query_lower)) - {"what", "is", "the", "are", "how", "when", "who", "which"}
        relevant_sentences = []

        for c, s, cit in retrieval_results[:3]:
            sentences = re.split(r"(?<=[.!?])\s+", c.content)
            for sent in sentences:
                sent_clean = sent.strip()
                if not sent_clean:
                    continue
                matches = sum(1 for w in query_words if w in sent_clean.lower())
                if matches > 0:
                    relevant_sentences.append((matches, cit.document_name, sent_clean))

        relevant_sentences.sort(key=lambda x: x[0], reverse=True)

        if relevant_sentences:
            sents_text = "\n\n".join([f"- **{src}**: {text}" for _, src, text in relevant_sentences[:4]])
            answer = (
                f"Based on **{citation.document_name}** and related project artifacts, here is the relevant intelligence:\n\n"
                f"{sents_text}\n\n"
                f"*Context excerpt from {citation.document_name}*:\n> \"{citation.excerpt}\""
            )
        else:
            answer = (
                f"According to **{citation.document_name}**:\n\n"
                f"> \"{citation.excerpt}\"\n\n"
                f"This matches your query with a retrieval relevance score of {score:.2f}."
            )

        return answer

    def _generate_suggested_followups(self, query: str, citations: List[Citation]) -> List[str]:
        q_lower = query.lower()
        if "risk" in q_lower:
            return [
                "What are the mitigation strategies for the highest severity risks?",
                "Which deliverables are threatened by technical dependencies?",
                "What is our estimated schedule delay?",
            ]
        elif "block" in q_lower or "impediment" in q_lower:
            return [
                "Who are the assigned owners for the open critical blockers?",
                "What action items are due before the next sprint review?",
                "How do these blockers impact our Milestone 1 deliverables?",
            ]
        elif "scope" in q_lower or "deliverable" in q_lower:
            return [
                "What features are officially designated as out-of-scope?",
                "What are the acceptance criteria for the core deliverables?",
                "What missing documentation gaps were identified?",
            ]
        else:
            return [
                "What are the top project risks identified so far?",
                "Are there any active blockers stalling the team?",
                "What is our current project health score breakdown?",
            ]
