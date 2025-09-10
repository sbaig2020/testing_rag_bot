# 🤖 AI RAG Bot - Intelligent Document Assistant

> **Transform your documents into an intelligent knowledge base with AI-powered conversations**

A powerful AI chatbot that combines **Retrieval-Augmented Generation (RAG)** with **Anthropic's Claude AI** to help you interact with your documents naturally. Upload your files, ask questions, and get intelligent answers with source citations.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Anthropic](https://img.shields.io/badge/AI-Claude%203-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 What This Project Does

**AI RAG Bot** turns your document collection into an intelligent assistant that can:

- 📚 **Understand Your Documents**: Upload PDFs, Word docs, text files, and more
- 🧠 **Answer Questions**: Ask anything about your documents in natural language  
- 🔍 **Find Information**: Semantic search across your entire knowledge base
- 📝 **Cite Sources**: Get answers with exact references to source documents
- 💬 **Chat Naturally**: Real-time conversation interface with typing indicators
- 📊 **Track Usage**: Monitor your document collection and chat statistics

### 🌟 Perfect For:
- **Researchers** analyzing papers and reports
- **Students** studying from textbooks and notes  
- **Professionals** working with manuals and documentation
- **Anyone** who wants to chat with their documents!

## 🚀 Quick Start (3 Steps!)

### 1. **Get Your API Key**
- Sign up at [Anthropic Console](https://console.anthropic.com/)
- Create an API key (you'll get free credits to start!)

### 2. **Setup & Install**
```bash
# Clone or download this repository
cd ai-rag-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

### 3. **Run & Enjoy!**
```bash
python app.py
```
Open http://localhost:5000 and start uploading documents!

## 📁 What's Inside This Project

### 🎮 **Multiple Ways to Run**
| File | Purpose | Best For |
|------|---------|----------|
| `app.py` | **Full-featured web app** | Complete experience with UI |
| `app_simple.py` | **Lightweight version** | Basic functionality, faster setup |
| `quick_start.py` | **Interactive guide** | First-time users |
| `demo.py` | **Feature demonstration** | Exploring capabilities |
| `start.py` | **Guided setup** | Step-by-step configuration |

### 🧠 **Core AI Components**
| File | What It Does |
|------|-------------|
| `chat_manager.py` | Handles AI conversations and RAG logic |
| `chat_manager_free.py` | Alternative using free APIs |
| `document_processor.py` | Extracts text from various file formats |
| `vector_store.py` | Manages document embeddings and search |

### ⚙️ **Configuration Options**
| File | Purpose |
|------|---------|
| `config.py` | Main configuration settings |
| `config_simple.py` | Simplified configuration |
| `free_api_config.py` | Free API alternatives |
| `.env.example` | Environment variables template |

### 🧪 **Testing & Validation**
| File | What It Tests |
|------|--------------|
| `test_installation.py` | Verifies setup is working |
| `test_openai_rag.py` | Tests OpenAI integration |
| `test_openrouter_rag.py` | Tests OpenRouter integration |
| `quick_rag_test.py` | Quick RAG functionality test |

### 📦 **Installation Options**
| File | Dependencies | Use Case |
|------|-------------|----------|
| `requirements.txt` | **Full features** | Complete installation |
| `requirements_simple.txt` | **Core features** | Minimal setup |
| `requirements_minimal.txt` | **Basic only** | Lightweight version |

## 🎨 **User Interface**

### **Web Interface** (`templates/` & `static/`)
- **Modern Design**: Clean, responsive interface
- **Real-time Chat**: WebSocket-powered messaging
- **Drag & Drop**: Easy file uploads
- **Dark Mode**: Automatic theme detection
- **Mobile Friendly**: Works on all devices

### **Key Features**
- 📤 **Document Upload**: Drag & drop multiple files
- 💬 **Chat Sessions**: Multiple conversations
- 🔍 **Document Search**: Find specific information
- 📊 **Statistics**: Usage analytics and insights
- ⚙️ **Settings**: Customize AI behavior
- 📥 **Export**: Save conversations in multiple formats

## 📄 **Supported File Types**

| Format | Extensions | Examples |
|--------|------------|----------|
| **PDF** | `.pdf` | Research papers, reports, manuals |
| **Word** | `.docx`, `.doc` | Documents, letters, proposals |
| **Text** | `.txt`, `.md` | Notes, documentation, code |
| **Web** | `.html`, `.htm` | Web pages, articles |
| **Data** | `.csv`, `.json` | Spreadsheets, structured data |

## 🔧 **Configuration Guide**

### **Environment Variables** (`.env` file)
```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Customization
FLASK_ENV=development
MAX_CHUNK_SIZE=1000          # Document chunk size
CHUNK_OVERLAP=200            # Overlap between chunks
MAX_TOKENS=4000              # AI response length
TEMPERATURE=0.7              # AI creativity (0-1)
MAX_FILE_SIZE=52428800       # 50MB upload limit
```

### **AI Model Options**
- **Claude 3 Haiku**: Fast, cost-effective
- **Claude 3 Sonnet**: Balanced performance  
- **Claude 3 Opus**: Most capable, slower

## 🎯 **Usage Examples**

### **Research & Analysis**
```
"What are the main findings in this research paper?"
"Compare the methodologies across these studies"
"What evidence supports the conclusion?"
```

### **Document Q&A**
```
"What are the key terms in this contract?"
"When is the project deadline?"
"What are the system requirements?"
```

### **Learning & Study**
```
"Explain this concept in simple terms"
"What are the important formulas?"
"Create a summary of chapter 5"
```

## 🏗️ **Architecture Overview**

```
📁 Your Documents
    ↓ (Upload)
📄 Document Processor → 🔤 Text Extraction
    ↓
🧮 Vector Store → 🔍 Embeddings & Search
    ↓
🤖 AI Chat Manager → 💬 Claude API
    ↓
🌐 Web Interface → 👤 You!
```

## 🚀 **Advanced Usage**

### **API Endpoints**
- `GET /api/health` - System status
- `POST /api/upload` - Upload documents
- `POST /api/chat` - Send messages
- `GET /api/documents` - List documents
- `POST /api/search` - Search documents

### **Customization**
- **System Prompts**: Customize AI behavior
- **Chunk Settings**: Optimize for your document types
- **Search Parameters**: Adjust retrieval accuracy
- **UI Themes**: Modify appearance

## 🔒 **Security & Privacy**

- ✅ **API Keys**: Stored securely in environment variables
- ✅ **File Validation**: Type and size restrictions
- ✅ **Local Processing**: Documents processed locally
- ✅ **No Data Sharing**: Your documents stay private

## 🐛 **Troubleshooting**

### **Common Issues**

**"Module not found" errors**
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**"API key not found"**
- Check `.env` file exists
- Verify `ANTHROPIC_API_KEY` is set correctly
- Ensure API key has sufficient credits

**Upload failures**
- Check file size (default 50MB limit)
- Verify file format is supported
- Ensure sufficient disk space

**Performance issues**
- Reduce `MAX_CHUNK_SIZE` for faster processing
- Use `requirements_simple.txt` for lighter installation
- Clear vector database: `rm -rf data/vector_db`

## 📊 **Performance & Resources**

### **System Requirements**
- **Python**: 3.8 or higher
- **RAM**: 2GB+ (4GB+ recommended)
- **Storage**: 1GB+ for vector database
- **Internet**: For AI API calls

### **Resource Usage**
- **Base Memory**: ~500MB
- **Per 1000 Documents**: +100MB
- **Vector Database**: Grows with collection
- **API Costs**: ~$0.01-0.10 per conversation

## 🤝 **Contributing**

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_installation.py

# Start development server
python app.py
```

## 📚 **Additional Resources**

- 📖 **Documentation**: Check the `/docs` folder (coming soon)
- 🎥 **Video Tutorials**: [YouTube Playlist](https://youtube.com) (coming soon)
- 💬 **Community**: [Discord Server](https://discord.gg) (coming soon)
- 🐛 **Issues**: [GitHub Issues](https://github.com/sbaig2020/testing_rag_bot/issues)

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

Built with amazing open-source technologies:

- 🧠 **[Anthropic](https://anthropic.com)** - Claude AI models
- 🔍 **[ChromaDB](https://chromadb.com)** - Vector database
- 🤗 **[Sentence Transformers](https://sbert.net)** - Text embeddings
- 🌐 **[Flask](https://flask.palletsprojects.com)** - Web framework
- ⚡ **[Socket.IO](https://socket.io)** - Real-time communication

## 🎉 **Ready to Start?**

1. **Get your API key** from Anthropic
2. **Run the quick setup**: `python quick_start.py`
3. **Start the app**: `python app.py`
4. **Upload documents** and start chatting!

---

**Questions? Issues? Suggestions?**  
Open an issue or start a discussion - we're here to help! 🚀

**Built with ❤️ for the AI community**
