"""
Retrieval-Augmented Generation (RAG) service for P&ID analysis.
Provides intelligent Q&A capabilities using extracted diagram data and knowledge base.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from backend.models import Graph, Node, Text, Issue

class RAGService:
    """
    Retrieval-Augmented Generation service for P&ID analysis.
    Combines extracted diagram data with knowledge base to answer natural language queries.
    """
    
    def __init__(self, knowledge_base_path: str = "backend/data/knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.embedding_model = None
        self.embeddings_cache = {}
        self._initialize_embedding_model()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base from JSON file."""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Knowledge base not found at {self.knowledge_base_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing knowledge base: {e}")
            return {}
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model for embeddings."""
        try:
            # Use a lightweight model for demo purposes
            print("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            import traceback
            traceback.print_exc()
            self.embedding_model = None
    
    def _create_knowledge_embeddings(self) -> Dict[str, np.ndarray]:
        """Create embeddings for all knowledge base entries."""
        if not self.embedding_model:
            return {}
        
        embeddings = {}
        
        # Process instrument tags
        for tag, info in self.knowledge_base.get('instrument_tags', {}).items():
            text = f"{tag}: {info.get('description', '')} {info.get('function', '')}"
            embeddings[f"tag_{tag}"] = self.embedding_model.encode(text)
        
        # Process equipment
        for equipment, info in self.knowledge_base.get('equipment', {}).items():
            text = f"{equipment}: {info.get('description', '')} {info.get('function', '')}"
            embeddings[f"equipment_{equipment}"] = self.embedding_model.encode(text)
        
        # Process process logic
        for logic, info in self.knowledge_base.get('process_logic', {}).items():
            text = f"{logic}: {info.get('description', '')} {info.get('control_strategy', '')}"
            embeddings[f"logic_{logic}"] = self.embedding_model.encode(text)
        
        # Process safety systems
        for safety, info in self.knowledge_base.get('safety_systems', {}).items():
            text = f"{safety}: {info.get('description', '')} {info.get('function', '')}"
            embeddings[f"safety_{safety}"] = self.embedding_model.encode(text)
        
        # Process common issues
        for issue, info in self.knowledge_base.get('common_issues', {}).items():
            text = f"{issue}: {info.get('description', '')} {info.get('impact', '')}"
            embeddings[f"issue_{issue}"] = self.embedding_model.encode(text)
        
        return embeddings
    
    def _retrieve_relevant_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant knowledge base entries for a given query.
        Uses cosine similarity between query embedding and knowledge base embeddings.
        """
        if not self.embedding_model:
            # Fallback to keyword matching
            return self._keyword_search(query, top_k)
        
        # Create embeddings if not cached
        if not self.embeddings_cache:
            self.embeddings_cache = self._create_knowledge_embeddings()
        
        # Encode the query
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate similarities
        similarities = []
        for key, embedding in self.embeddings_cache.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((key, similarity))
        
        # Sort by similarity and get top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:top_k]
        
        # Retrieve the actual knowledge base entries
        relevant_knowledge = []
        for key, similarity in top_matches:
            if similarity > 0.3:  # Minimum similarity threshold
                knowledge_entry = self._get_knowledge_entry(key)
                if knowledge_entry:
                    knowledge_entry['similarity'] = similarity
                    relevant_knowledge.append(knowledge_entry)
        
        return relevant_knowledge
    
    def _keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Fallback keyword search when embeddings are not available."""
        query_lower = query.lower()
        matches = []
        
        # Search instrument tags
        for tag, info in self.knowledge_base.get('instrument_tags', {}).items():
            score = 0
            if tag.lower() in query_lower:
                score += 2
            if any(word in info.get('description', '').lower() for word in query_lower.split()):
                score += 1
            if score > 0:
                matches.append({
                    'type': 'instrument_tag',
                    'key': tag,
                    'data': info,
                    'similarity': score / 3.0
                })
        
        # Search equipment
        for equipment, info in self.knowledge_base.get('equipment', {}).items():
            score = 0
            if equipment.lower() in query_lower:
                score += 2
            if any(word in info.get('description', '').lower() for word in query_lower.split()):
                score += 1
            if score > 0:
                matches.append({
                    'type': 'equipment',
                    'key': equipment,
                    'data': info,
                    'similarity': score / 3.0
                })
        
        # Sort by score and return top-k
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches[:top_k]
    
    def _get_knowledge_entry(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge base entry by key."""
        if key.startswith('tag_'):
            tag = key[4:]
            return {
                'type': 'instrument_tag',
                'key': tag,
                'data': self.knowledge_base.get('instrument_tags', {}).get(tag, {})
            }
        elif key.startswith('equipment_'):
            equipment = key[10:]
            return {
                'type': 'equipment',
                'key': equipment,
                'data': self.knowledge_base.get('equipment', {}).get(equipment, {})
            }
        elif key.startswith('logic_'):
            logic = key[6:]
            return {
                'type': 'process_logic',
                'key': logic,
                'data': self.knowledge_base.get('process_logic', {}).get(logic, {})
            }
        elif key.startswith('safety_'):
            safety = key[7:]
            return {
                'type': 'safety_system',
                'key': safety,
                'data': self.knowledge_base.get('safety_systems', {}).get(safety, {})
            }
        elif key.startswith('issue_'):
            issue = key[6:]
            return {
                'type': 'common_issue',
                'key': issue,
                'data': self.knowledge_base.get('common_issues', {}).get(issue, {})
            }
        return None
    
    def _extract_context_from_graph(self, graph: Graph) -> str:
        """Extract relevant context from the analyzed P&ID graph."""
        context_parts = []
        
        # Extract symbol information
        symbols_info = []
        for node in graph.nodes:
            if node.kind in ['equipment', 'instrument']:
                symbol_info = f"- {node.type} (ID: {node.id})"
                if node.tag:
                    symbol_info += f" with tag: {node.tag}"
                if node.confidence:
                    symbol_info += f" (confidence: {node.confidence:.2f})"
                symbols_info.append(symbol_info)
        
        if symbols_info:
            context_parts.append("Detected symbols and equipment:")
            context_parts.extend(symbols_info)
        
        # Extract text information
        text_info = []
        for text in graph.texts:
            if text.content.strip():
                text_info.append(f"- '{text.content}' at position ({text.bbox.x}, {text.bbox.y})")
        
        if text_info:
            context_parts.append("\nDetected text elements:")
            context_parts.extend(text_info)
        
        # Extract issues
        issues_info = []
        for issue in graph.issues:
            issues_info.append(f"- {issue.severity.upper()}: {issue.message}")
        
        if issues_info:
            context_parts.append("\nIdentified issues:")
            context_parts.extend(issues_info)
        
        return "\n".join(context_parts)
    
    def _generate_llm_response(self, query: str, context: str, relevant_knowledge: List[Dict[str, Any]]) -> str:
        """
        Generate a response using an LLM (OpenAI GPT or local model).
        """
        # Prepare the knowledge base information
        kb_info = []
        for item in relevant_knowledge:
            kb_text = f"{item['type']}: {item['key']}\n"
            if isinstance(item['data'], dict):
                for key, value in item['data'].items():
                    if isinstance(value, list):
                        kb_text += f"  {key}: {', '.join(map(str, value))}\n"
                    else:
                        kb_text += f"  {key}: {value}\n"
            kb_info.append(kb_text)
        
        knowledge_text = "\n".join(kb_info)
        
        # Create the prompt
        prompt = f"""You are an expert P&ID (Piping and Instrumentation Diagram) analyst. 
Answer the user's question about the P&ID diagram based on the extracted information and knowledge base.

P&ID Analysis Context:
{context}

Relevant Knowledge Base Information:
{knowledge_text}

User Question: {query}

Please provide a clear, technical answer that:
1. Directly addresses the user's question
2. References specific elements from the P&ID analysis when relevant
3. Uses information from the knowledge base to provide accurate technical details
4. Mentions any issues or concerns identified in the diagram
5. Provides practical insights for process engineers

Answer:"""
        
        try:
            # Try OpenAI API first
            if os.getenv('OPENAI_API_KEY'):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert P&ID analyst with deep knowledge of industrial processes and instrumentation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            else:
                # Fallback to simple rule-based response
                return self._generate_fallback_response(query, context, relevant_knowledge)
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_response(query, context, relevant_knowledge)
    
    def _generate_fallback_response(self, query: str, context: str, relevant_knowledge: List[Dict[str, Any]]) -> str:
        """Generate a fallback response when LLM is not available."""
        response_parts = []
        
        # Check if query is about a specific tag
        tag_match = re.search(r'([A-Z]{2,3})-?(\d+)', query.upper())
        if tag_match:
            tag_prefix = tag_match.group(1)
            tag_number = tag_match.group(2)
            
            # Find matching knowledge
            for item in relevant_knowledge:
                if item['type'] == 'instrument_tag' and item['key'] == tag_prefix:
                    data = item['data']
                    response_parts.append(f"Tag {tag_prefix}-{tag_number} refers to a {data.get('description', 'instrument')}.")
                    response_parts.append(f"Function: {data.get('function', 'Not specified')}")
                    if data.get('typical_use'):
                        response_parts.append(f"Typical use: {data.get('typical_use')}")
                    if data.get('fault_modes'):
                        response_parts.append(f"Common issues: {', '.join(data.get('fault_modes', []))}")
                    break
        
        # Check if query is about equipment
        equipment_keywords = ['pump', 'valve', 'tank', 'heat exchanger', 'instrument']
        for keyword in equipment_keywords:
            if keyword.lower() in query.lower():
                for item in relevant_knowledge:
                    if item['type'] == 'equipment' and keyword.lower() in item['key'].lower():
                        data = item['data']
                        response_parts.append(f"{item['key'].title()} is {data.get('description', 'equipment')}.")
                        response_parts.append(f"Function: {data.get('function', 'Not specified')}")
                        break
        
        # Check for issues in the context
        if "issues:" in context.lower():
            response_parts.append("The diagram analysis identified some issues that should be addressed.")
        
        if not response_parts:
            response_parts.append("Based on the P&ID analysis, I can see various process equipment and instrumentation.")
            if relevant_knowledge:
                response_parts.append("Here's what I found in the knowledge base:")
                for item in relevant_knowledge[:3]:  # Show top 3 matches
                    response_parts.append(f"- {item['key']}: {item['data'].get('description', 'No description available')}")
        
        return "\n".join(response_parts)
    
    def answer_query(self, query: str, graph: Graph) -> Dict[str, Any]:
        """
        Main method to answer a natural language query about a P&ID diagram.
        
        Args:
            query: Natural language question about the diagram
            graph: Analyzed P&ID graph with extracted symbols, text, and issues
            
        Returns:
            Dictionary containing the answer and metadata
        """
        try:
            # Extract context from the graph
            context = self._extract_context_from_graph(graph)
            
            # Retrieve relevant knowledge
            relevant_knowledge = self._retrieve_relevant_knowledge(query, top_k=5)
            
            # Generate response
            answer = self._generate_llm_response(query, context, relevant_knowledge)
            
            # Prepare response metadata
            response = {
                'answer': answer,
                'query': query,
                'context_used': context,
                'knowledge_sources': [
                    {
                        'type': item['type'],
                        'key': item['key'],
                        'similarity': item.get('similarity', 0.0)
                    }
                    for item in relevant_knowledge
                ],
                'confidence': self._calculate_response_confidence(relevant_knowledge, context)
            }
            
            return response
            
        except Exception as e:
            return {
                'answer': f"Error processing query: {str(e)}",
                'query': query,
                'context_used': "",
                'knowledge_sources': [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _calculate_response_confidence(self, relevant_knowledge: List[Dict[str, Any]], context: str) -> float:
        """Calculate confidence score for the response."""
        if not relevant_knowledge:
            return 0.1
        
        # Base confidence on knowledge similarity scores
        avg_similarity = np.mean([item.get('similarity', 0.0) for item in relevant_knowledge])
        
        # Boost confidence if context is rich
        context_richness = min(len(context.split()) / 100.0, 1.0)
        
        # Combine factors
        confidence = (avg_similarity * 0.7) + (context_richness * 0.3)
        return min(confidence, 1.0)

# Global RAG service instance
rag_service = RAGService()

def answer_pid_query(query: str, graph: Graph) -> Dict[str, Any]:
    """
    Convenience function to answer a P&ID query using the global RAG service.
    
    Args:
        query: Natural language question
        graph: Analyzed P&ID graph
        
    Returns:
        Response dictionary with answer and metadata
    """
    try:
        # Try using the full RAG service
        return rag_service.answer_query(query, graph)
    except Exception as e:
        print(f"Error in RAG service: {e}, falling back to simple response")
        # Fallback to a very simple response when the full RAG service fails
        return {
            'answer': generate_simple_fallback_response(query, graph),
            'query': query,
            'context_used': "Error in RAG processing - using fallback response",
            'knowledge_sources': [],
            'confidence': 0.1,
            'error': str(e)
        }

def generate_simple_fallback_response(query: str, graph: Graph) -> str:
    """Generate a very simple fallback response when the RAG service fails completely."""
    
    response_parts = []
    
    # Count nodes by type
    node_types = {}
    for node in graph.nodes:
        if node.type in node_types:
            node_types[node.type] += 1
        else:
            node_types[node.type] = 1
    
    # Add basic analysis information
    response_parts.append(f"Based on the diagram analysis, I can see:")
    
    # Mention symbols
    if node_types:
        for node_type, count in node_types.items():
            response_parts.append(f"- {count} {node_type}{'s' if count > 1 else ''}")
    else:
        response_parts.append("- No symbols were detected in the diagram")
    
    # Mention text elements
    if graph.texts:
        response_parts.append(f"- {len(graph.texts)} text elements")
        
        # List a few examples if available (up to 3)
        if len(graph.texts) > 0:
            response_parts.append("Some text in the diagram includes:")
            for text in graph.texts[:3]:  # Show up to 3 text elements
                if text.content.strip():
                    response_parts.append(f"  * {text.content}")
    else:
        response_parts.append("- No text was detected in the diagram")
    
    # Mention connections
    if graph.edges:
        response_parts.append(f"- {len(graph.edges)} connections between elements")
    
    # Mention issues
    if graph.issues:
        response_parts.append(f"- {len(graph.issues)} issues were identified")
        # Show up to 3 issues
        for issue in graph.issues[:3]:
            response_parts.append(f"  * {issue.severity.upper()}: {issue.message}")
    
    return "\n".join(response_parts)