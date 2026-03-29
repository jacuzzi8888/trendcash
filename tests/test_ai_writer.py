import pytest
from unittest.mock import patch, MagicMock
from app.ai_writer import (
    configure_gemini, generate_article, improve_content,
    generate_headline, generate_excerpt, generate_faqs, test_connection,
    GEMINI_AVAILABLE
)


class TestConfigureGemini:
    def test_configure_without_key_returns_error(self):
        # When no API key is provided and none in env, should return error
        with patch.dict('os.environ', {'GEMINI_API_KEY': '', 'GOOGLE_API_KEY': ''}):
            result = configure_gemini()
            assert result['success'] == False
            # Could be either error depending on whether gemini is installed
            assert 'error' in result
    
    def test_configure_with_key_when_available(self):
        if not GEMINI_AVAILABLE:
            pytest.skip("google-generativeai not installed")
        
        with patch('app.ai_writer.genai') as mock_genai:
            result = configure_gemini('test-key')
            mock_genai.configure.assert_called_once_with(api_key='test-key')


class TestGenerateArticle:
    def test_generate_article_no_api_key(self):
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': False, 'error': 'No key'}
            result = generate_article('Test topic', [])
            assert result['success'] == False
    
    def test_generate_article_success(self):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '# Generated Article\n\nContent here...'
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': True}
            with patch('app.ai_writer.get_model') as mock_get_model:
                mock_get_model.return_value = mock_model
                
                result = generate_article(
                    topic='Test Topic',
                    sources=[{'publisher': 'CNN', 'url': 'https://cnn.com'}],
                    category='News'
                )
                
                assert result['success'] == True
                assert result['topic'] == 'Test Topic'
                assert 'Generated Article' in result['content']


class TestImproveContent:
    def test_improve_content_success(self):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'Improved content here'
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': True}
            with patch('app.ai_writer.get_model') as mock_get_model:
                mock_get_model.return_value = mock_model
                
                result = improve_content('Original content', 'Make it better')
                
                assert result['success'] == True
                assert 'improved_at' in result


class TestGenerateHeadline:
    def test_generate_headline_success(self):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "1. First Headline\n2. Second Headline\n3. Third Headline"
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': True}
            with patch('app.ai_writer.get_model') as mock_get_model:
                mock_get_model.return_value = mock_model
                
                result = generate_headline('Test Topic', 'news')
                
                assert result['success'] == True
                assert len(result['headlines']) >= 1


class TestGenerateExcerpt:
    def test_generate_excerpt_success(self):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'This is a short excerpt.'
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': True}
            with patch('app.ai_writer.get_model') as mock_get_model:
                mock_get_model.return_value = mock_model
                
                result = generate_excerpt('Long article content...' * 100, max_length=160)
                
                assert result['success'] == True
                assert len(result['excerpt']) <= 160


class TestGenerateFaqs:
    def test_generate_faqs_success(self):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "1. Q: What is this?\n   A: This is a test."
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': True}
            with patch('app.ai_writer.get_model') as mock_get_model:
                mock_get_model.return_value = mock_model
                
                result = generate_faqs('Test Topic', 'Some context')
                
                assert result['success'] == True
                assert 'faqs' in result


class TestTestConnection:
    def test_test_connection_success(self):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Connection successful"
        mock_model.generate_content.return_value = mock_response
        
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': True}
            with patch('app.ai_writer.get_model') as mock_get_model:
                mock_get_model.return_value = mock_model
                
                result = test_connection()
                
                assert result['success'] == True
    
    def test_test_connection_failure(self):
        with patch('app.ai_writer.configure_gemini') as mock_config:
            mock_config.return_value = {'success': False, 'error': 'No API key'}
            result = test_connection()
            assert result['success'] == False
