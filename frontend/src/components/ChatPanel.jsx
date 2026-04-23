import { MoreVertical, SlidersHorizontal, Paperclip, ChevronDown, ChevronUp, Info, ArrowUpRight, BookOpen, FileText, MessageSquare, Share2, Copy, Check } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { useState, useRef, useEffect } from 'react';
import { ragAPI } from '../lib/api';

function MessageBubble({ message }) {
  const [showSources, setShowSources] = useState(false);

  if (message.role === 'user') {
    return (
      <div className="ml-auto max-w-[85%] sm:max-w-[80%]">
        <div className="rounded-lg p-3 sm:p-4 bg-card border border-border">
          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>
    );
  }

  if (message.error) {
    return (
      <div className="rounded-lg p-3 sm:p-4 bg-destructive/20 border border-destructive">
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
      </div>
    );
  }

  // Convert markdown-style formatting to rich formatted text
  const formatContent = (content) => {
    if (!content) return null;

    const lines = content.split('\n');
    const elements = [];
    let currentParagraph = [];
    let inList = false;

    const processInlineFormatting = (text) => {
      const parts = [];
      let lastIndex = 0;
      
      // Match **bold** text
      const boldRegex = /\*\*(.+?)\*\*/g;
      let match;
      
      while ((match = boldRegex.exec(text)) !== null) {
        if (match.index > lastIndex) {
          parts.push(text.substring(lastIndex, match.index));
        }
        parts.push(<strong key={`bold-${match.index}`} className="font-semibold text-foreground">{match[1]}</strong>);
        lastIndex = match.index + match[0].length;
      }
      
      if (lastIndex < text.length) {
        parts.push(text.substring(lastIndex));
      }
      
      return parts.length > 0 ? parts : text;
    };

    const detectTable = (lines, startIdx) => {
      // Detect markdown tables: | Header | Header |
      const tableLines = [];
      let idx = startIdx;
      
      while (idx < lines.length && lines[idx].includes('|')) {
        tableLines.push(lines[idx]);
        idx++;
      }
      
      if (tableLines.length >= 2) {
        return { lines: tableLines, endIdx: idx };
      }
      return null;
    };

    const renderTable = (tableLines, key) => {
      const rows = tableLines.map(line => 
        line.split('|').map(cell => cell.trim()).filter(cell => cell !== '')
      );
      
      // Skip separator row (second row with dashes)
      const headerRow = rows[0];
      const dataRows = rows.slice(2);
      
      return (
        <div key={key} className="my-4 overflow-x-auto">
          <table className="w-full border-collapse border border-border text-sm">
            <thead className="bg-card">
              <tr>
                {headerRow.map((header, idx) => (
                  <th key={idx} className="border border-border px-3 py-2 text-left font-semibold">
                    {processInlineFormatting(header)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataRows.map((row, rowIdx) => (
                <tr key={rowIdx} className={rowIdx % 2 === 0 ? 'bg-card/50' : 'bg-background'}>
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx} className="border border-border px-3 py-2">
                      {processInlineFormatting(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    };

    let skipUntil = -1;

    lines.forEach((line, idx) => {
      // Skip lines that are part of a table
      if (idx < skipUntil) return;

      // Check for table
      if (line.includes('|')) {
        const tableData = detectTable(lines, idx);
        if (tableData) {
          if (currentParagraph.length > 0) {
            elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
            currentParagraph = [];
          }
          inList = false;
          elements.push(renderTable(tableData.lines, `table-${idx}`));
          skipUntil = tableData.endIdx;
          return;
        }
      }

      // Main headers with ## (larger, bold)
      if (line.match(/^##\s+\*\*/)) {
        if (currentParagraph.length > 0) {
          elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
          currentParagraph = [];
        }
        inList = false;
        const text = line.replace(/^##\s+\*\*(.+?)\*\*:?/, '$1');
        elements.push(
          <h2 key={`h2-${idx}`} className="text-xl font-bold mb-3 mt-5 text-primary border-b border-border pb-2">
            {text}
          </h2>
        );
      }
      // Section headers with **text** on new line
      else if (line.match(/^\*\*[^:]+:\*\*$/)) {
        if (currentParagraph.length > 0) {
          elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
          currentParagraph = [];
        }
        inList = false;
        const text = line.replace(/^\*\*(.+?):\*\*$/, '$1');
        elements.push(
          <h3 key={`h3-${idx}`} className="text-base font-bold mb-2 mt-4 text-foreground">
            {text}:
          </h3>
        );
      }
      // Numbered lists with bold
      else if (line.match(/^\d+\.\s+/)) {
        if (currentParagraph.length > 0) {
          elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
          currentParagraph = [];
        }
        inList = true;
        const number = line.match(/^\d+/)[0];
        const content = line.replace(/^\d+\.\s+/, '');
        elements.push(
          <div key={`nl-${idx}`} className="mb-2 flex gap-3 text-sm">
            <span className="font-semibold text-primary shrink-0">{number}.</span>
            <span className="leading-relaxed">{processInlineFormatting(content)}</span>
          </div>
        );
      }
      // Bullet points
      else if (line.match(/^[•\*\-]\s+/)) {
        if (currentParagraph.length > 0) {
          elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
          currentParagraph = [];
        }
        inList = true;
        const content = line.replace(/^[•\*\-]\s+/, '');
        elements.push(
          <div key={`b-${idx}`} className="mb-2 flex gap-3 text-sm">
            <span className="text-primary shrink-0 font-bold">•</span>
            <span className="leading-relaxed">{processInlineFormatting(content)}</span>
          </div>
        );
      }
      // Nested bullet points (with indentation)
      else if (line.match(/^\s+[•\*\-]\s+/)) {
        if (currentParagraph.length > 0) {
          elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
          currentParagraph = [];
        }
        const indent = line.match(/^\s*/)[0].length;
        const content = line.replace(/^\s+[•\*\-]\s+/, '');
        const marginLeft = Math.floor(indent / 2) * 12;
        elements.push(
          <div key={`nb-${idx}`} className="mb-1.5 flex gap-3 text-sm" style={{ marginLeft: `${marginLeft}px` }}>
            <span className="text-muted-foreground shrink-0">◦</span>
            <span className="leading-relaxed">{processInlineFormatting(content)}</span>
          </div>
        );
      }
      // Empty lines
      else if (line.trim() === '') {
        if (currentParagraph.length > 0) {
          elements.push(<p key={`p-${idx}`} className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
          currentParagraph = [];
        }
        if (inList) {
          elements.push(<div key={`sp-${idx}`} className="h-2" />);
          inList = false;
        }
      }
      // Regular text
      else {
        if (inList) {
          elements.push(<div key={`sp-${idx}`} className="h-2" />);
          inList = false;
        }
        currentParagraph.push(line.trim() + ' ');
      }
    });

    // Add remaining paragraph
    if (currentParagraph.length > 0) {
      elements.push(<p key="p-final" className="mb-3 text-sm leading-relaxed">{currentParagraph.map(processInlineFormatting)}</p>);
    }

    return elements;
  };

  return (
    <div className="space-y-2">
      <div className="bg-card border border-border rounded-lg p-5">
        <div className="text-sm leading-relaxed">
          {formatContent(message.content)}
        </div>
      </div>
      
      {message.sources && message.sources.length > 0 && (
        <div className="space-y-2">
          <button
            onClick={() => setShowSources(!showSources)}
            className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:bg-card rounded border border-border transition-colors"
          >
            {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            <span className="font-medium">
              References ({message.sources.length})
            </span>
          </button>
          
          {showSources && (
            <div className="bg-card border border-border rounded-lg p-4">
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <FileText size={16} className="text-primary" />
                References
              </h4>
              <div className="space-y-2">
                {message.sources.map((source, idx) => (
                  <div key={idx} className="text-xs bg-background p-3 rounded border border-border">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <span className="font-medium text-foreground">
                        [{idx + 1}] {source.source}
                      </span>
                      {source.rerank_score && (
                        <Badge variant="outline" className="text-xs shrink-0">
                          {(source.rerank_score * 100).toFixed(0)}%
                        </Badge>
                      )}
                    </div>
                    {source.excerpt && (
                      <div className="text-muted-foreground mt-1.5 italic text-xs leading-relaxed">
                        "{source.excerpt}"
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ChatPanel({ sources, stats, onClearChat }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef(null);
  const scrollRef = useRef(null);

  // Clear messages when onClearChat is triggered externally
  useEffect(() => {
    const clearMessages = () => setMessages([]);
    // Listen for clear event
    window.addEventListener('clearChat', clearMessages);
    return () => window.removeEventListener('clearChat', clearMessages);
  }, []);

  // Trigger message clear when sources are cleared
  useEffect(() => {
    if (sources.length === 0 && messages.length > 0) {
      setMessages([]);
    }
  }, [sources.length]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleQuickAction = async (action) => {
    let prompt = '';
    if (action === 'summary') {
      prompt = 'Provide a comprehensive summary of all the uploaded documents.';
    } else if (action === 'qna') {
      prompt = `You are an expert at extracting structured Q&A from technical documents.

Generate high-quality, concise, and technically accurate questions and answers from the provided documents.

Follow these rules:

• Only create questions based on content that actually exists in the documents.
• Each question must be exam-friendly, clear, and specific.
• Answers must be short, precise, and directly supported by the text.
• Do not hallucinate or assume anything beyond what is given.
• Format the output cleanly using numbered questions.
• Use bold formatting only for questions and section headings.
• Do not use any decorative symbols or special characters.

Extract the Q&A from the uploaded documents.`;
    }
    
    if (!prompt) return;
    
    const userMessage = { role: 'user', content: prompt };
    setMessages([...messages, userMessage]);
    setIsLoading(true);
    
    try {
      const result = await ragAPI.askQuestion(prompt);
      
      const assistantMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.sources || [],
        metadata: result.metadata
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Query failed:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`,
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Wrap user query with structured Q&A extraction prompt
    const enhancedPrompt = `You are an expert at extracting structured Q&A from technical documents.

Generate high-quality, concise, and technically accurate questions and answers from the provided documents.

Follow these rules:

• Only create questions based on content that actually exists in the documents.
• Each question must be exam-friendly, clear, and specific.
• Answers must be short, precise, and directly supported by the text.
• Do not hallucinate or assume anything beyond what is given.
• Format the output cleanly using numbered questions.
• Use bold formatting only for questions and section headings.
• Do not use any decorative symbols or special characters.

Now answer the following query based on the documents:

QUERY START
${input}
QUERY END`;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const result = await ragAPI.askQuestion(enhancedPrompt);
      
      const assistantMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.sources || [],
        metadata: result.metadata
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Query failed:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`,
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShareChat = () => {
    if (messages.length === 0) return;
    setShowShareDialog(true);
  };

  const formatChatText = () => {
    return messages.map(msg => {
      if (msg.role === 'user') {
        return `You: ${msg.content}`;
      } else {
        let text = `Assistant: ${msg.content}`;
        if (msg.sources && msg.sources.length > 0) {
          text += '\n\nSources:\n' + msg.sources.map((s, idx) => 
            `[${idx + 1}] ${s.source}${s.excerpt ? ` - "${s.excerpt}"` : ''}`
          ).join('\n');
        }
        return text;
      }
    }).join('\n\n---\n\n');
  };

  const handleCopyChat = async () => {
    if (messages.length === 0) return;
    
    try {
      await navigator.clipboard.writeText(formatChatText());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
      alert('Failed to copy to clipboard');
    }
  };

  const handleDownloadTxt = () => {
    if (messages.length === 0) return;
    
    const chatText = formatChatText();
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowShareDialog(false);
  };

  const handleDownloadJson = () => {
    if (messages.length === 0) return;
    
    const exportData = {
      exportDate: new Date().toISOString(),
      messageCount: messages.length,
      sources: sources.map(s => s.name),
      conversation: messages
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowShareDialog(false);
  };

  const handleDownloadMarkdown = () => {
    if (messages.length === 0) return;
    
    let markdown = `# Chat Export\n\n**Date:** ${new Date().toLocaleString()}\n\n**Sources:** ${sources.map(s => s.name).join(', ') || 'None'}\n\n---\n\n`;
    
    messages.forEach((msg, idx) => {
      if (msg.role === 'user') {
        markdown += `### 💬 You\n\n${msg.content}\n\n`;
      } else {
        markdown += `### 🤖 Assistant\n\n${msg.content}\n\n`;
        if (msg.sources && msg.sources.length > 0) {
          markdown += `**Sources:**\n\n`;
          msg.sources.forEach((s, sIdx) => {
            markdown += `${sIdx + 1}. ${s.source}${s.excerpt ? ` - *"${s.excerpt}"*` : ''}\n`;
          });
          markdown += '\n';
        }
      }
      if (idx < messages.length - 1) {
        markdown += '---\n\n';
      }
    });
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowShareDialog(false);
  };

  const handleDownloadPdf = () => {
    if (messages.length === 0) return;
    
    // Create a new window with the formatted content
    const printWindow = window.open('', '_blank');
    
    let qnaNumber = 1;
    let htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Q&A Export - ${new Date().toLocaleDateString()}</title>
        <style>
          @page {
            size: A4;
            margin: 2cm;
          }
          
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: white;
            padding: 20px;
            max-width: 210mm;
            margin: 0 auto;
          }
          
          .header {
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 25px;
          }
          
          .header h1 {
            font-size: 26px;
            font-weight: 700;
            color: #1e40af;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
          }
          
          .header .meta {
            font-size: 12px;
            color: #6b7280;
            margin-top: 6px;
            line-height: 1.6;
          }
          
          .header .meta strong {
            color: #374151;
            font-weight: 600;
          }
          
          .qna-item {
            margin-bottom: 30px;
            page-break-inside: avoid;
            border-left: 4px solid #e5e7eb;
            padding-left: 20px;
          }
          
          .question-section {
            margin-bottom: 15px;
          }
          
          .question-label {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #2563eb;
            margin-bottom: 8px;
          }
          
          .question-number {
            background: #2563eb;
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            min-width: 32px;
            text-align: center;
          }
          
          .question-text {
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            line-height: 1.5;
            margin-top: 6px;
          }
          
          .answer-section {
            margin-top: 12px;
          }
          
          .answer-label {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #059669;
            margin-bottom: 8px;
          }
          
          .answer-text {
            font-size: 14px;
            color: #374151;
            line-height: 1.8;
            text-align: justify;
          }
          
          .answer-text strong {
            font-weight: 700;
            color: #1f2937;
          }
          
          .answer-text h2 {
            font-size: 18px;
            font-weight: 700;
            color: #1e40af;
            margin-top: 16px;
            margin-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 6px;
          }
          
          .answer-text h3 {
            font-size: 15px;
            font-weight: 700;
            color: #1f2937;
            margin-top: 14px;
            margin-bottom: 8px;
          }
          
          .answer-text p {
            margin-bottom: 10px;
          }
          
          .numbered-list {
            margin: 12px 0;
            padding-left: 0;
          }
          
          .numbered-list-item {
            display: flex;
            gap: 12px;
            margin-bottom: 10px;
            align-items: flex-start;
          }
          
          .list-number {
            font-weight: 700;
            color: #2563eb;
            font-size: 14px;
            min-width: 24px;
            flex-shrink: 0;
          }
          
          .list-content {
            flex: 1;
            line-height: 1.7;
          }
          
          .bullet-list {
            margin: 12px 0 12px 15px;
          }
          
          .bullet-item {
            display: flex;
            gap: 10px;
            margin-bottom: 8px;
            align-items: flex-start;
          }
          
          .bullet {
            color: #2563eb;
            font-weight: 700;
            font-size: 16px;
            flex-shrink: 0;
          }
          
          .sources {
            margin-top: 15px;
            padding: 12px;
            background: #f9fafb;
            border-radius: 6px;
            border-left: 4px solid #fbbf24;
          }
          
          .sources-title {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: #92400e;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
          }
          
          .source-item {
            font-size: 12px;
            color: #4b5563;
            margin-bottom: 4px;
            line-height: 1.5;
          }
          
          .source-number {
            color: #f59e0b;
            font-weight: 700;
          }
          
          .page-break {
            page-break-after: always;
          }
          
          .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            font-size: 11px;
            color: #9ca3af;
          }
          
          table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 13px;
          }
          
          table th {
            background: #f3f4f6;
            padding: 10px;
            text-align: left;
            font-weight: 700;
            color: #1f2937;
            border: 1px solid #d1d5db;
          }
          
          table td {
            padding: 8px 10px;
            border: 1px solid #e5e7eb;
            color: #374151;
          }
          
          table tr:nth-child(even) {
            background: #f9fafb;
          }
          
          .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 120px;
            font-weight: 900;
            color: rgba(37, 99, 235, 0.08);
            letter-spacing: 20px;
            z-index: -1;
            pointer-events: none;
            user-select: none;
            font-family: 'Arial Black', sans-serif;
          }
          
          @media print {
            body {
              padding: 0;
            }
            
            .qna-item {
              page-break-inside: avoid;
            }
            
            .watermark {
              position: fixed;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%) rotate(-45deg);
              font-size: 120px;
              font-weight: 900;
              color: rgba(37, 99, 235, 0.08);
              letter-spacing: 20px;
              z-index: -1;
            }
          }
        </style>
      </head>
      <body>
        <div class="watermark">TULLS</div>
        <div class="header">
          <h1>Questions & Answers</h1>
          <div class="meta">
            <strong>Date:</strong> ${new Date().toLocaleString()}<br>
            <strong>Total Q&A:</strong> ${Math.floor(messages.length / 2)}<br>
            ${sources.length > 0 ? `<strong>Sources:</strong> ${sources.map(s => s.name).join(', ')}` : ''}
          </div>
        </div>
        
        <div class="content">
    `;
    
    // Process messages in pairs (question + answer)
    for (let i = 0; i < messages.length; i++) {
      const msg = messages[i];
      
      if (msg.role === 'user') {
        htmlContent += `
          <div class="qna-item">
            <div class="question-section">
              <div class="question-label">
                <span class="question-number">Q${qnaNumber}</span>
                <span>QUESTION</span>
              </div>
              <div class="question-text">${msg.content}</div>
            </div>
        `;
        
        // Check for corresponding answer
        if (i + 1 < messages.length && messages[i + 1].role === 'assistant') {
          const answerMsg = messages[i + 1];
          
          htmlContent += `
            <div class="answer-section">
              <div class="answer-label">ANSWER</div>
              <div class="answer-text">
          `;
          
          // Format the answer content
          const lines = answerMsg.content.split('\n');
          let inNumberedList = false;
          let inBulletList = false;
          let currentParagraph = [];
          
          lines.forEach(line => {
            // Headers with ##
            if (line.match(/^##\s+\*\*/)) {
              if (currentParagraph.length > 0) {
                htmlContent += `<p>${currentParagraph.join(' ')}</p>`;
                currentParagraph = [];
              }
              if (inNumberedList) { htmlContent += '</div>'; inNumberedList = false; }
              if (inBulletList) { htmlContent += '</div>'; inBulletList = false; }
              
              const text = line.replace(/^##\s+\*\*(.+?)\*\*:?/, '$1');
              htmlContent += `<h2>${text}</h2>`;
            }
            // Section headers with **text:**
            else if (line.match(/^\*\*[^:]+:\*\*$/)) {
              if (currentParagraph.length > 0) {
                htmlContent += `<p>${currentParagraph.join(' ')}</p>`;
                currentParagraph = [];
              }
              if (inNumberedList) { htmlContent += '</div>'; inNumberedList = false; }
              if (inBulletList) { htmlContent += '</div>'; inBulletList = false; }
              
              const text = line.replace(/^\*\*(.+?):\*\*$/, '$1');
              htmlContent += `<h3>${text}:</h3>`;
            }
            // Numbered lists
            else if (line.match(/^\d+\.\s+/)) {
              if (currentParagraph.length > 0) {
                htmlContent += `<p>${currentParagraph.join(' ')}</p>`;
                currentParagraph = [];
              }
              if (inBulletList) { htmlContent += '</div>'; inBulletList = false; }
              if (!inNumberedList) {
                htmlContent += '<div class="numbered-list">';
                inNumberedList = true;
              }
              
              const number = line.match(/^\d+/)[0];
              const content = line.replace(/^\d+\.\s+/, '').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
              htmlContent += `
                <div class="numbered-list-item">
                  <span class="list-number">${number}.</span>
                  <span class="list-content">${content}</span>
                </div>
              `;
            }
            // Bullet points
            else if (line.match(/^[•\*\-]\s+/)) {
              if (currentParagraph.length > 0) {
                htmlContent += `<p>${currentParagraph.join(' ')}</p>`;
                currentParagraph = [];
              }
              if (inNumberedList) { htmlContent += '</div>'; inNumberedList = false; }
              if (!inBulletList) {
                htmlContent += '<div class="bullet-list">';
                inBulletList = true;
              }
              
              const content = line.replace(/^[•\*\-]\s+/, '').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
              htmlContent += `
                <div class="bullet-item">
                  <span class="bullet">•</span>
                  <span>${content}</span>
                </div>
              `;
            }
            // Empty lines
            else if (line.trim() === '') {
              if (currentParagraph.length > 0) {
                htmlContent += `<p>${currentParagraph.join(' ')}</p>`;
                currentParagraph = [];
              }
              if (inNumberedList) { htmlContent += '</div>'; inNumberedList = false; }
              if (inBulletList) { htmlContent += '</div>'; inBulletList = false; }
            }
            // Regular text
            else {
              if (inNumberedList) { htmlContent += '</div>'; inNumberedList = false; }
              if (inBulletList) { htmlContent += '</div>'; inBulletList = false; }
              
              const formatted = line.trim().replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
              currentParagraph.push(formatted);
            }
          });
          
          // Close any remaining elements
          if (currentParagraph.length > 0) {
            htmlContent += `<p>${currentParagraph.join(' ')}</p>`;
          }
          if (inNumberedList) htmlContent += '</div>';
          if (inBulletList) htmlContent += '</div>';
          
          htmlContent += `</div>`;
          
          // Add sources if available
          if (answerMsg.sources && answerMsg.sources.length > 0) {
            htmlContent += `
              <div class="sources">
                <div class="sources-title">References</div>
            `;
            answerMsg.sources.forEach((source, idx) => {
              htmlContent += `
                <div class="source-item">
                  <span class="source-number">[${idx + 1}]</span> ${source.source}
                </div>
              `;
            });
            htmlContent += `</div>`;
          }
          
          htmlContent += `</div>`;
          i++; // Skip the answer message in next iteration
        }
        
        htmlContent += `</div>`;
        qnaNumber++;
      }
    }
    
    htmlContent += `
        </div>
        
        <div class="footer">
          Generated on ${new Date().toLocaleString()} | Total ${qnaNumber - 1} Q&A pairs
        </div>
      </body>
      </html>
    `;
    
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    
    // Wait for content to load then trigger print
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print();
        printWindow.onafterprint = () => printWindow.close();
      }, 250);
    };
    
    setShowShareDialog(false);
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0 || !input.trim()) return;

    // Wrap user query with structured Q&A extraction prompt
    const enhancedPrompt = `You are an expert at extracting structured Q&A from technical documents.

Generate high-quality, concise, and technically accurate questions and answers from the provided documents.

Follow these rules:

• Only create questions based on content that actually exists in the documents.
• Each question must be exam-friendly, clear, and specific.
• Answers must be short, precise, and directly supported by the text.
• Do not hallucinate or assume anything beyond what is given.
• Format the output cleanly using numbered questions.
• Use bold formatting only for questions and section headings.
• Do not use any decorative symbols or special characters.

Now answer the following query based on the documents:

QUERY START
${input}
QUERY END`;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const result = await ragAPI.uploadAndAsk(Array.from(files), enhancedPrompt, true);
      
      const assistantMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.sources || [],
        metadata: result.metadata
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Upload and query failed:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`,
        error: true
      }]);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* Share Dialog */}
      {showShareDialog && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="bg-card border-2 border-border rounded-lg shadow-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <Share2 size={20} className="text-primary" />
              Export Chat
            </h3>
            <p className="text-sm text-muted-foreground mb-6">
              Choose how you'd like to export your conversation ({messages.length} messages)
            </p>
            
            <div className="space-y-2 mb-6">
              <Button
                variant="default"
                onClick={handleDownloadPdf}
                className="w-full justify-start gap-3 bg-primary hover:bg-primary/90"
              >
                <FileText size={18} />
                <div className="flex flex-col items-start flex-1">
                  <span className="font-medium">Download as PDF</span>
                  <span className="text-xs opacity-90">Well-formatted Q&A document</span>
                </div>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleCopyChat}
                className="w-full justify-start gap-3"
              >
                {copied ? (
                  <>
                    <Check size={18} className="text-green-500" />
                    <span>Copied to Clipboard!</span>
                  </>
                ) : (
                  <>
                    <Copy size={18} />
                    <div className="flex flex-col items-start flex-1">
                      <span className="font-medium">Copy to Clipboard</span>
                      <span className="text-xs text-muted-foreground">Plain text format</span>
                    </div>
                  </>
                )}
              </Button>
              
              <Button
                variant="outline"
                onClick={handleDownloadTxt}
                className="w-full justify-start gap-3"
              >
                <FileText size={18} />
                <div className="flex flex-col items-start flex-1">
                  <span className="font-medium">Download as TXT</span>
                  <span className="text-xs text-muted-foreground">Simple text file</span>
                </div>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleDownloadMarkdown}
                className="w-full justify-start gap-3"
              >
                <FileText size={18} />
                <div className="flex flex-col items-start flex-1">
                  <span className="font-medium">Download as Markdown</span>
                  <span className="text-xs text-muted-foreground">Formatted .md file</span>
                </div>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleDownloadJson}
                className="w-full justify-start gap-3"
              >
                <FileText size={18} />
                <div className="flex flex-col items-start flex-1">
                  <span className="font-medium">Download as JSON</span>
                  <span className="text-xs text-muted-foreground">Structured data with metadata</span>
                </div>
              </Button>
            </div>
            
            <div className="flex justify-end">
              <Button
                variant="ghost"
                onClick={() => setShowShareDialog(false)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between px-3 sm:px-4 md:px-6 py-3 md:py-4 border-b border-border">
        <div className="flex items-center gap-1 sm:gap-2">
          <h2 className="text-base sm:text-lg font-semibold">Chat</h2>
          <Button variant="ghost" size="icon" className="w-6 h-6 hidden sm:flex">
            <Info size={16} className="text-muted-foreground" />
          </Button>
        </div>
        <div className="flex items-center gap-1 sm:gap-2">
          <Button 
            variant="ghost" 
            size="icon"

            onClick={handleShareChat}
            disabled={messages.length === 0}
            title="Share chat"
            className="cursor-pointer w-8 h-8 sm:w-10 sm:h-10"
          >
            <Share2 size={16} className="sm:w-[18px] sm:h-[18px]" />
          </Button>
          <Button variant="ghost" size="icon" className="hidden md:flex">
            <SlidersHorizontal size={18} />
          </Button>
          <Button variant="ghost" size="icon" className="w-8 h-8 sm:w-10 sm:h-10">
            <MoreVertical size={16} className="sm:w-[18px] sm:h-[18px]" />
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="max-w-3xl mx-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6 md:py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[300px] sm:min-h-[400px] text-center">
              <div className="mb-4 sm:mb-6">
                <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-3 sm:mb-4 bg-card border-2 border-border rounded-2xl flex items-center justify-center">
                  <BookOpen size={32} className="text-primary sm:w-10 sm:h-10" />
                </div>
                <h3 className="text-xl sm:text-2xl font-semibold mb-2">Untitled notebook</h3>
                <p className="text-sm text-muted-foreground mb-4 sm:mb-6">
                  {sources.length} source{sources.length !== 1 ? 's' : ''}
                </p>
                
                {sources.length > 0 && (
                  <div className="flex flex-col gap-2 sm:gap-3 mt-4 sm:mt-6">
                    <p className="text-xs text-muted-foreground mb-1 sm:mb-2">Quick Actions</p>
                    <div className="flex gap-2 sm:gap-3 justify-center">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction('summary')}
                        disabled={isLoading}
                        className="gap-2"
                      >
                        <FileText size={14} className="sm:w-4 sm:h-4" />
                        <span className="text-xs sm:text-sm">Summary</span>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickAction('qna')}
                        disabled={isLoading}
                        className="gap-2"
                      >
                        <MessageSquare size={14} className="sm:w-4 sm:h-4" />
                        <span className="text-xs sm:text-sm">Q&A</span>
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-4 sm:space-y-6">
              {messages.map((msg, idx) => (
                <MessageBubble key={idx} message={msg} />
              ))}
              
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                  <span className="text-sm">Thinking...</span>
                </div>
              )}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t border-border p-2 sm:p-3 md:p-4">
        <div className="max-w-3xl mx-auto flex items-center gap-1 sm:gap-2">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.txt,.md,.docx"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="w-8 h-8 sm:w-10 sm:h-10 shrink-0"
            title="Upload documents"
          >
            <Paperclip size={16} className="sm:w-[18px] sm:h-[18px]" />
          </Button>
          <div className="flex-1 relative min-w-0">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
              placeholder="Start typing..."
              disabled={isLoading}
              className="pr-16 sm:pr-20 md:pr-24 bg-card border-border text-sm sm:text-base"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-0.5 sm:gap-1">
              <span className="text-xs text-muted-foreground hidden xs:inline">
                {stats?.documents_in_kb || 0} docs
              </span>
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="icon"
                variant="ghost"
                className="w-7 h-7 sm:w-8 sm:h-8 shrink-0"
              >
                <ArrowUpRight size={16} className="sm:w-[18px] sm:h-[18px]" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
