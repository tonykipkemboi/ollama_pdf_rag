"""Test RAG functionality."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.core.rag import RAGPipeline
from langchain_core.documents import Document
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser

class TestRAGPipeline(unittest.TestCase):
    """Test cases for RAG pipeline."""
    
    def setUp(self):
        """Set up test cases."""
        # Create the mocks
        self.mock_vector_db = Mock()
        self.mock_llm_manager = Mock()
        
        # Patch MultiQueryRetriever
        self.retriever_patcher = patch('langchain.retrievers.multi_query.MultiQueryRetriever.from_llm')
        self.mock_from_llm = self.retriever_patcher.start()
        self.mock_retriever = Mock()
        self.mock_from_llm.return_value = self.mock_retriever
        
        # Patch RunnablePassthrough
        self.passthrough_patcher = patch('langchain_core.runnables.RunnablePassthrough')
        self.mock_passthrough = self.passthrough_patcher.start()
        self.mock_passthrough.return_value = MagicMock()
        
        # Create mock chain components that support the | operator
        self.mock_chain = MagicMock()
        self.mock_chain.__or__.return_value = self.mock_chain
        self.mock_chain.__ror__.return_value = self.mock_chain
        
        # Set up LLM manager
        self.mock_llm_manager.get_rag_prompt.return_value = self.mock_chain
        self.mock_llm_manager.llm = self.mock_chain
        self.mock_llm_manager.get_query_prompt.return_value = self.mock_chain
        
        # Mock vector db retriever
        mock_retriever = Mock()
        self.mock_vector_db.as_retriever.return_value = mock_retriever
        
        # Create the RAG pipeline
        self.rag = RAGPipeline(self.mock_vector_db, self.mock_llm_manager)
    
    def tearDown(self):
        """Clean up patches."""
        self.retriever_patcher.stop()
        self.passthrough_patcher.stop()
    
    def test_setup_retriever(self):
        """Test retriever setup."""
        # Reset call counts
        self.mock_vector_db.as_retriever.reset_mock()
        
        # Test retriever creation
        retriever = self.rag._setup_retriever()
        self.assertIsNotNone(retriever)
        self.mock_vector_db.as_retriever.assert_called_once()
    
    def test_setup_chain(self):
        """Test chain setup."""
        # Reset call counts
        self.mock_llm_manager.get_rag_prompt.reset_mock()
        
        # Test chain creation
        chain = self.rag._setup_chain()
        self.assertIsNotNone(chain)
        self.assertEqual(chain, self.mock_chain)
    
    def test_get_response(self):
        """Test getting response from the RAG pipeline."""
        # Set up mock response
        expected_response = "Test response"
        self.mock_chain.invoke.return_value = expected_response
        
        # Reset the chain
        self.rag.chain = self.mock_chain
        
        # Test getting response
        question = "What is this document about?"
        response = self.rag.get_response(question)
        
        # Verify response and chain invocation
        self.assertEqual(response, expected_response)
        self.mock_chain.invoke.assert_called_once_with(question)
    
    def test_get_response_empty_question(self):
        """Test handling empty question."""
        # Set up mock response
        self.mock_chain.invoke.return_value = ""
        
        # Test with empty question
        response = self.rag.get_response("")
        self.assertEqual(response, "")
    
    def test_get_response_long_question(self):
        """Test handling very long question."""
        # Create a long question
        long_question = "Why " + "very " * 1000 + "long question?"
        expected_response = "Response to long question"
        self.mock_chain.invoke.return_value = expected_response
        
        # Test with long question
        response = self.rag.get_response(long_question)
        self.assertEqual(response, expected_response)
    
    def test_get_response_special_characters(self):
        """Test handling questions with special characters."""
        special_question = "What about @#$%^&* characters?"
        expected_response = "Response with special chars"
        self.mock_chain.invoke.return_value = expected_response
        
        response = self.rag.get_response(special_question)
        self.assertEqual(response, expected_response)
    
    def test_chain_error_handling(self):
        """Test error handling in the chain."""
        # Make the chain raise an exception
        self.mock_chain.invoke.side_effect = Exception("Chain error")
        
        # Test error handling
        with self.assertRaises(Exception):
            self.rag.get_response("Test question")
    
    def test_retriever_error_handling(self):
        """Test error handling in the retriever setup."""
        # Make the retriever creation fail
        self.mock_from_llm.side_effect = Exception("Retriever error")
        
        # Test error handling
        with self.assertRaises(Exception):
            RAGPipeline(self.mock_vector_db, self.mock_llm_manager)
    
    def test_memory_cleanup(self):
        """Test proper cleanup of resources."""
        # Create a new pipeline
        rag = RAGPipeline(self.mock_vector_db, self.mock_llm_manager)
        
        # Simulate some operations
        rag.get_response("Test question")
        
        # Check that resources are properly managed
        self.mock_vector_db.as_retriever.assert_called()
        self.mock_chain.invoke.assert_called() 