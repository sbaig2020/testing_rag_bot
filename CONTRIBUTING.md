# Contributing to AI RAG Bot

Thank you for your interest in contributing to AI RAG Bot! We welcome contributions from the community and are pleased to have you join us.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Anthropic API key (for testing)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/testing_rag_bot.git
   cd testing_rag_bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

5. **Run tests**
   ```bash
   python test_installation.py
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

### Project Structure
```
ai-rag-bot/
├── app.py                 # Main Flask application
├── chat_manager.py        # AI conversation management
├── document_processor.py  # Document parsing and processing
├── vector_store.py        # Vector database operations
├── config.py             # Configuration management
├── static/               # CSS, JS, and other static files
├── templates/            # HTML templates
└── tests/                # Test files
```

### Coding Standards

#### Python Code
```python
def process_document(file_path: str, chunk_size: int = 1000) -> List[str]:
    """
    Process a document and return text chunks.
    
    Args:
        file_path: Path to the document file
        chunk_size: Maximum size of each text chunk
        
    Returns:
        List of text chunks
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If chunk_size is invalid
    """
    # Implementation here
    pass
```

#### Error Handling
- Always handle exceptions appropriately
- Use specific exception types
- Log errors with appropriate detail
- Provide meaningful error messages to users

#### Configuration
- Use environment variables for sensitive data
- Provide sensible defaults
- Document all configuration options

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python test_installation.py

# Run with coverage
python -m pytest --cov=.
```

### Writing Tests
- Write tests for all new functionality
- Include both positive and negative test cases
- Test edge cases and error conditions
- Use descriptive test names

Example test:
```python
def test_document_processor_handles_pdf():
    """Test that PDF files are processed correctly."""
    processor = DocumentProcessor()
    chunks = processor.process_file("test.pdf")
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
```

## 📝 Pull Request Process

### Before Submitting
1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python test_installation.py
   python -m pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new document processing feature"
   ```

### Commit Message Format
Use conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding tests
- `refactor:` for code refactoring
- `style:` for formatting changes

Examples:
```
feat: add support for EPUB document processing
fix: resolve memory leak in vector store
docs: update installation instructions
test: add unit tests for chat manager
```

### Pull Request Guidelines
1. **Fill out the PR template completely**
2. **Link related issues** using keywords like "Fixes #123"
3. **Provide clear description** of changes and motivation
4. **Include screenshots** for UI changes
5. **Ensure all tests pass**
6. **Request review** from maintainers

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🐛 Bug Reports

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if it's already fixed
3. **Check the troubleshooting guide** in README.md

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS, Windows, Linux]
- Python version: [e.g. 3.9.0]
- Browser: [e.g. Chrome, Firefox]
- Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Additional document format support (EPUB, RTF, etc.)
- [ ] Performance optimizations for large document collections
- [ ] Enhanced search capabilities
- [ ] Mobile app development
- [ ] API rate limiting and caching

### Medium Priority
- [ ] Additional AI model integrations
- [ ] Advanced analytics and reporting
- [ ] User authentication and multi-tenancy
- [ ] Batch document processing
- [ ] Export/import functionality

### Good First Issues
- [ ] UI/UX improvements
- [ ] Documentation enhancements
- [ ] Test coverage improvements
- [ ] Code refactoring
- [ ] Bug fixes

## 📚 Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Community
- [GitHub Discussions](https://github.com/sbaig2020/testing_rag_bot/discussions)
- [Issues](https://github.com/sbaig2020/testing_rag_bot/issues)

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks in documentation

## 📞 Getting Help

If you need help:
1. Check the [README.md](README.md) for setup instructions
2. Search [existing issues](https://github.com/sbaig2020/testing_rag_bot/issues)
3. Create a new issue with the "question" label
4. Join our community discussions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI RAG Bot! 🚀
