#!/usr/bin/env python3
"""
AI RAG Bot Quick Start Guide
This script provides a quick setup and demonstration of the AI RAG Bot
"""

import os
import sys
import time
from pathlib import Path

def print_header():
    """Print the header"""
    print("\n" + "="*60)
    print("🚀 AI RAG BOT - QUICK START GUIDE")
    print("="*60)

def check_setup():
    """Check if the setup is complete"""
    print("🔍 Checking setup...")
    
    # Check if .env file exists and has API key
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_anthropic_api_key_here" in content:
            print("⚠️  API key not configured")
            return False
    
    print("✅ Setup looks good!")
    return True

def show_features():
    """Show key features"""
    print("\n🌟 KEY FEATURES:")
    print("-" * 40)
    
    features = [
        "🧠 Advanced AI Chat with Claude 3 models",
        "📚 RAG (Retrieval-Augmented Generation)",
        "📄 Multi-format document support",
        "💬 Real-time chat interface",
        "🔍 Semantic document search",
        "📊 Usage statistics and analytics",
        "🎨 Modern responsive UI",
        "📤 Export conversations",
        "⚙️ Customizable settings",
        "🔒 Secure API key management"
    ]
    
    for feature in features:
        print(f"  {feature}")
        time.sleep(0.1)

def show_supported_formats():
    """Show supported document formats"""
    print("\n📄 SUPPORTED DOCUMENT FORMATS:")
    print("-" * 40)
    
    formats = [
        ("PDF", "Research papers, reports, manuals"),
        ("DOCX", "Microsoft Word documents"),
        ("TXT", "Plain text files"),
        ("MD", "Markdown documentation"),
        ("HTML", "Web pages and HTML files"),
        ("CSV", "Data files and spreadsheets"),
        ("JSON", "Structured data files")
    ]
    
    for format_type, description in formats:
        print(f"  {format_type:<6} {description}")
        time.sleep(0.1)

def show_usage_workflow():
    """Show typical usage workflow"""
    print("\n🔄 TYPICAL WORKFLOW:")
    print("-" * 40)
    
    steps = [
        "1. 📤 Upload Documents",
        "   • Drag & drop files to upload area",
        "   • Files are automatically processed",
        "   • Text is extracted and chunked",
        "   • Embeddings are generated",
        "",
        "2. 💬 Start Chatting",
        "   • Create a new chat session",
        "   • Ask questions about your documents",
        "   • AI retrieves relevant context",
        "   • Get answers with source citations",
        "",
        "3. 🔍 Advanced Features",
        "   • Search documents semantically",
        "   • Adjust AI model settings",
        "   • Export conversations",
        "   • Manage multiple sessions"
    ]
    
    for step in steps:
        print(f"  {step}")
        time.sleep(0.1)

def show_example_queries():
    """Show example queries"""
    print("\n💡 EXAMPLE QUERIES:")
    print("-" * 40)
    
    examples = [
        "📚 Research Questions:",
        "   • 'What are the main findings in this research?'",
        "   • 'Summarize the methodology used'",
        "   • 'What are the limitations mentioned?'",
        "",
        "📋 Document Analysis:",
        "   • 'What are the key terms in this contract?'",
        "   • 'Extract all the important dates'",
        "   • 'What are the main requirements?'",
        "",
        "📊 Data Insights:",
        "   • 'What patterns do you see in this data?'",
        "   • 'What are the trends over time?'",
        "   • 'Identify any anomalies'",
        "",
        "🔍 Information Retrieval:",
        "   • 'How do I configure feature X?'",
        "   • 'What are the troubleshooting steps?'",
        "   • 'Find information about topic Y'"
    ]
    
    for example in examples:
        print(f"  {example}")
        time.sleep(0.1)

def show_tips():
    """Show usage tips"""
    print("\n💡 USAGE TIPS:")
    print("-" * 40)
    
    tips = [
        "🎯 Be Specific: Ask detailed questions for better results",
        "📝 Use Context: Reference specific documents or sections",
        "🔄 Iterate: Refine your questions based on responses",
        "📊 Check Sources: Review cited sources for accuracy",
        "⚙️ Adjust Settings: Experiment with different AI parameters",
        "💾 Save Sessions: Export important conversations",
        "🔍 Search First: Use document search to find relevant content",
        "📤 Organize Files: Use descriptive filenames for uploads"
    ]
    
    for tip in tips:
        print(f"  {tip}")
        time.sleep(0.1)

def show_next_steps():
    """Show next steps"""
    print("\n🚀 NEXT STEPS:")
    print("-" * 40)
    
    if not check_setup():
        print("  1. Configure your Anthropic API key in .env file")
        print("  2. Run: python start.py")
        print("  3. Follow the guided setup")
    else:
        print("  1. Run: python app.py")
        print("  2. Open http://localhost:5000 in your browser")
        print("  3. Upload some documents")
        print("  4. Start chatting with your AI assistant!")
    
    print("\n📚 Additional Resources:")
    print("  • README.md - Comprehensive documentation")
    print("  • demo.py - Interactive feature demonstration")
    print("  • test_installation.py - Verify installation")

def main():
    """Main function"""
    print_header()
    
    sections = [
        ("Features", show_features),
        ("Supported Formats", show_supported_formats),
        ("Workflow", show_usage_workflow),
        ("Example Queries", show_example_queries),
        ("Tips", show_tips),
        ("Next Steps", show_next_steps)
    ]
    
    for section_name, section_func in sections:
        try:
            section_func()
            if section_name != "Next Steps":  # Don't pause after last section
                input(f"\nPress Enter to continue to {sections[sections.index((section_name, section_func)) + 1][0]}...")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Quick start guide interrupted")
            break
        except IndexError:
            break
    
    print("\n" + "="*60)
    print("🎉 READY TO START!")
    print("="*60)
    print("Your AI RAG Bot is ready to help you explore and")
    print("understand your documents with advanced AI capabilities!")
    print("="*60)

if __name__ == "__main__":
    main()
