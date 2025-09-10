# 🤖 AI RAG Bot - Intelligent Document Assistant

> **Transform your documents into an intelligent, conversational AI assistant**

A powerful AI chatbot with **Retrieval-Augmented Generation (RAG)** capabilities that lets you chat with your documents using advanced AI models. Upload your files, ask questions, and get intelligent responses with source citations.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 What This Project Does

**AI RAG Bot** is your personal document assistant that:
- 📚 **Ingests your documents** (PDFs, Word docs, text files, etc.)
- 🧠 **Understands content** using advanced AI embeddings
- 💬 **Answers questions** about your documents intelligently
- 🔍 **Provides source citations** so you know where answers come from
- 🌐 **Works through a web interface** - no technical knowledge required

### Perfect For:
- 📖 **Students** - Chat with textbooks, research papers, lecture notes
- 💼 **Professionals** - Query reports, manuals, documentation
- 🔬 **Researchers** - Explore large document collections
- 📝 **Writers** - Reference and analyze source materials
- 🏢 **Teams** - Create searchable knowledge bases

## ✨ Key Features

### 🚀 Core Capabilities
| Feature | Description |
|---------|-------------|
| **Smart Document Chat** | Ask questions about your uploaded documents in natural language |
| **Multi-Format Support** | PDF, DOCX, TXT, MD, HTML, CSV, JSON files supported |
| **Source Citations** | Every answer includes references to source documents |
| **Semantic Search** | Find relevant information across your entire document collection |
| **Real-Time Interface** | Modern web UI with live chat and typing indicators |

### 🎛️ Advanced Features
- **Multiple AI Models**: Choose from Claude 3 Sonnet, Haiku, or Opus
- **Customizable Settings**: Adjust AI temperature, response length, system prompts
- **Session Management**: Multiple chat sessions with full history
- **Export Options**: Save conversations as JSON, TXT, or Markdown
- **Usage Analytics**: Track document count, sessions, and system metrics
- **Dark/Light Mode**: Automatic theme detection

## 🏗️ Project Structure

```
ai-rag-bot/
├── 📱 Web Application
│   ├── app.py                 # Main Flask application
│   ├── templates/             # HTML templates
│   └── static/               # CSS, JS, and assets
│
├── 🧠 AI & RAG System
│   ├── chat_manager.py       # AI conversation handling
│   ├── document_processor.py # Document parsing and chunking
│   ├── vector_store.py       # Vector database operations
│   └── config.py            # Configuration management
│
├── 🚀 Quick Start Options
│   ├── quick_start.py        # Interactive setup guide
│   ├── demo.py              # Feature demonstration
│   ├── app_simple.py        # Simplified version
│   └── start.py             # Guided setup wizard
│
├── 🔧 Configuration & Setup
│   ├── requirements.txt      # Full dependencies
│   ├── requirements_simple.txt # Minimal dependencies
│   ├── .env.example         # Environment template
│   └── setup_free_api.py    # Free API alternatives
│
├── 🧪 Testing & Validation
│   ├── test_installation.py # Verify setup
│   ├── test_openai_rag.py  # OpenAI integration test
│   └── quick_rag_test.py   # RAG functionality test
│
└── 📊 Data & Logs
    ├── data/vector_db/      # Vector database storage
    ├── static/uploads/      # Uploaded documents
    └── logs/               # Application logs
```

## 🚀 Quick Start (3 Steps)

### 1️⃣ **Get the Code**
```bash
git clone https://github.com/sbaig2020/testing_rag_bot.git
cd testing_rag_bot/ai-rag-bot
```

### 2️⃣ **Setup Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3️⃣ **Launch & Use**
```bash
# Start the application
python app.py

# Open http://localhost:5000 in your browser
# Upload documents and start chatting!
```

## 🎮 Multiple Ways to Run

| Method | Best For | Command |
|--------|----------|---------|
| **Full Version** | Complete features | `python app.py` |
| **Simple Version** | Basic functionality | `python app_simple.py` |
| **Quick Start** | First-time users | `python quick_start.py` |
| **Demo Mode** | Feature exploration | `python demo.py` |
| **Guided Setup** | Step-by-step setup | `python start.py` |

## 📋 Requirements & Setup

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 2GB+ RAM (for AI models)
- **Storage**: 1GB+ free space
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### API Requirements
- **Anthropic API Key** (Primary) - Get from [Anthropic Console](https://console.anthropic.com/)
- **OpenAI API Key** (Alternative) - For OpenAI models
- **OpenRouter API Key** (Alternative) - For multiple model access

### Environment Variables
Create a `.env` file with:
```env
# Required: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Alternative AI Providers
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Configuration
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 💡 How It Works

### 🔄 The RAG Process
1. **📤 Document Upload**: You upload files through the web interface
2. **✂️ Text Processing**: Documents are split into manageable chunks
3. **🧮 Embedding Generation**: AI creates vector representations of text
4. **💾 Vector Storage**: Embeddings stored in ChromaDB database
5. **❓ Question Processing**: Your questions are converted to embeddings
6. **🔍 Similarity Search**: System finds most relevant document chunks
7. **🤖 AI Response**: Claude generates answers using retrieved context
8. **📝 Citation**: Response includes source document references

### 🏛️ Architecture Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask Server   │◄──►│  Vector Store   │
│                 │    │                  │    │   (ChromaDB)    │
│ • Upload docs   │    │ • Process files  │    │ • Embeddings    │
│ • Chat interface│    │ • Handle queries │    │ • Similarity    │
│ • View results  │    │ • Manage sessions│    │   search        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AI Provider    │
                       │                  │
                       │ • Claude 3       │
                       │ • OpenAI GPT     │
                       │ • OpenRouter     │
                       └──────────────────┘
```

## 📚 Supported Document Types

| Format | Extensions | Use Cases |
|--------|------------|-----------|
| **PDF** | `.pdf` | Research papers, reports, manuals, books |
| **Word** | `.docx` | Documents, proposals, articles |
| **Text** | `.txt` | Notes, logs, plain text files |
| **Markdown** | `.md` | Documentation, README files |
| **HTML** | `.html`, `.htm` | Web pages, formatted documents |
| **CSV** | `.csv` | Data files, spreadsheets, tables |
| **JSON** | `.json` | Structured data, configuration files |

## 🎯 Example Use Cases

### 📖 **Academic Research**
```
Upload: Research papers, textbooks, lecture notes
Ask: "What are the main findings about climate change impacts?"
Get: Comprehensive answer with citations from multiple papers
```

### 💼 **Business Intelligence**
```
Upload: Reports, market analysis, company documents
Ask: "What were the key revenue drivers last quarter?"
Get: Data-driven insights with source references
```

### 🔧 **Technical Documentation**
```
Upload: API docs, user manuals, troubleshooting guides
Ask: "How do I configure the authentication system?"
Get: Step-by-step instructions with exact page references
```

### 📝 **Content Creation**
```
Upload: Source materials, research, reference documents
Ask: "What are the different perspectives on this topic?"
Get: Balanced overview with multiple source citations
```

## ⚙️ Configuration Options

### AI Model Settings
- **Model Selection**: Choose between Claude 3 Sonnet, Haiku, or Opus
- **Temperature**: Control creativity (0.0 = focused, 1.0 = creative)
- **Max Tokens**: Set response length limits
- **System Prompts**: Customize AI behavior and personality

### Document Processing
- **Chunk Size**: Adjust text splitting (default: 1000 characters)
- **Chunk Overlap**: Set overlap between chunks (default: 200 characters)
- **File Size Limits**: Configure maximum upload sizes
- **Supported Formats**: Enable/disable specific file types

### Interface Customization
- **Theme**: Auto, light, or dark mode
- **Language**: Interface language settings
- **Export Formats**: Choose available export options
- **Session Limits**: Set maximum concurrent sessions

## 🔒 Security & Privacy

### Data Protection
- **Local Processing**: Documents processed locally on your machine
- **API Security**: Secure communication with AI providers
- **No Data Retention**: AI providers don't store your documents
- **Environment Variables**: Sensitive keys stored securely

### Best Practices
- Keep your `.env` file private and never commit it to version control
- Use strong, unique API keys
- Regularly update dependencies for security patches
- Monitor API usage and costs
- Review uploaded documents for sensitive information

## 🐛 Troubleshooting

### Common Issues & Solutions

#### ❌ **"Module not found" errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### ❌ **"API key not found" error**
- Verify `.env` file exists in the project root
- Check that `ANTHROPIC_API_KEY` is set correctly
- Ensure no extra spaces or quotes around the key
- Verify API key is valid and has sufficient credits

#### ❌ **Upload failures**
- Check file size (default limit: 10MB)
- Verify file format is supported
- Ensure sufficient disk space
- Try uploading one file at a time

#### ❌ **Vector database issues**
```bash
# Clear and rebuild vector database
rm -rf data/vector_db
# Restart application - database will be recreated
python app.py
```

#### ❌ **Performance issues**
- Reduce chunk size for faster processing
- Close unused browser tabs
- Restart the application periodically
- Check available system memory

### Debug Mode
Enable detailed logging:
```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

Check logs at: `logs/app.log`

## 🚀 Advanced Usage

### Custom System Prompts
Customize AI behavior by modifying system prompts in the settings:
```
You are a helpful research assistant. Always provide detailed explanations 
and cite your sources. Focus on accuracy and clarity in your responses.
```

### Batch Document Processing
Upload multiple documents at once:
1. Select multiple files in the upload dialog
2. Wait for processing to complete
3. Documents are automatically indexed
4. Start asking questions across all documents

### API Integration
The application exposes REST endpoints for programmatic access:
- `POST /api/upload` - Upload documents
- `POST /api/chat` - Send chat messages
- `GET /api/documents` - List uploaded documents
- `DELETE /api/documents/{id}` - Remove documents

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/sbaig2020/testing_rag_bot.git
cd testing_rag_bot/ai-rag-bot

# Create development environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_installation.py
```

### Areas for Contribution
- 🌐 **Internationalization**: Add support for more languages
- 📱 **Mobile UI**: Improve mobile responsiveness
- 🔌 **Integrations**: Add support for more AI providers
- 📊 **Analytics**: Enhanced usage statistics and insights
- 🧪 **Testing**: Expand test coverage
- 📚 **Documentation**: Improve guides and examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Core Technologies
- **[Anthropic](https://www.anthropic.com/)** - Claude AI models
- **[ChromaDB](https://www.trychroma.com/)** - Vector database
- **[Sentence Transformers](https://www.sbert.net/)** - Text embeddings
- **[Flask](https://flask.palletsprojects.com/)** - Web framework
- **[Socket.IO](https://socket.io/)** - Real-time communication

### Community
- Thanks to all contributors and users who provide feedback
- Special thanks to the open-source AI and ML community
- Inspired by the growing RAG and document AI ecosystem

## 📞 Support & Community

### Getting Help
1. **📖 Documentation**: Check this README and inline code comments
2. **🐛 Issues**: Report bugs via [GitHub Issues](https://github.com/sbaig2020/testing_rag_bot/issues)
3. **💬 Discussions**: Join conversations in [GitHub Discussions](https://github.com/sbaig2020/testing_rag_bot/discussions)
4. **📧 Contact**: Reach out for specific questions or collaborations

### Useful Resources
- **[Anthropic API Documentation](https://docs.anthropic.com/)**
- **[ChromaDB Documentation](https://docs.trychroma.com/)**
- **[Flask Documentation](https://flask.palletsprojects.com/)**
- **[RAG Best Practices Guide](https://docs.anthropic.com/claude/docs/retrieval-augmented-generation)**

---

<div align="center">

**🌟 Star this repository if you find it helpful! 🌟**

**Built with ❤️ for the AI community**

[⬆ Back to Top](#-ai-rag-bot---intelligent-document-assistant)

</div>
