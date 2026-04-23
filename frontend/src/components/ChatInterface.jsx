import { useState, useRef, useEffect } from 'react';
import { FiSend, FiPaperclip, FiFileText } from 'react-icons/fi';
import { Card } from './ui/card';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';

export default function ChatInterface({ messages, setMessages }) {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        role: 'assistant',
        content:
          'Based on the provided documents, here is the information you requested. The documents discuss various topics related to your question.',
        sources: [
          { id: 1, title: 'Reference Chapter 3' },
          { id: 2, title: 'Reference Chapter 7' },
          { id: 3, title: 'Appendix B' },
          { id: 4, title: 'Index Section 12' },
        ],
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full dot-background">
      {/* Messages Area */}
      <ScrollArea className="flex-1 px-8 py-6" ref={scrollRef}>
        <div className="max-w-5xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-start justify-center h-full py-16">
              <div className="w-full max-w-3xl">
                <div className="mb-8 p-6 bg-card/50 border-l-4 border-primary">
                  <h2 className="text-xl font-bold uppercase tracking-wide mb-3">
                    Document Query Interface
                  </h2>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    This system enables semantic search across uploaded document collections using retrieval-augmented generation. 
                    Submit queries to retrieve relevant information with source citations.
                  </p>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="font-mono text-xs">
                      Status: Ready
                    </Badge>
                    <Badge variant="outline" className="font-mono text-xs">
                      Chunks: 6
                    </Badge>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-sm font-bold uppercase tracking-wide text-muted-foreground">
                    System Capabilities
                  </h3>
                  <div className="grid gap-3">
                    {[
                      'Multi-document context retrieval',
                      'Semantic similarity matching',
                      'Citation-backed responses',
                      'Cross-reference analysis',
                    ].map((item, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 bg-card/30 border border-border">
                        <div className="w-1.5 h-1.5 bg-primary mt-2 shrink-0" />
                        <span className="text-sm">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className="max-w-[85%]">
                  {/* Label */}
                  <div className="mb-2">
                    <Badge variant={message.role === 'user' ? 'default' : 'secondary'} className="text-xs font-mono">
                      {message.role === 'user' ? 'QUERY' : 'RESPONSE'}
                    </Badge>
                  </div>
                  
                  <Card
                    className={`${
                      message.role === 'user'
                        ? 'bg-primary/10 border-primary/30'
                        : 'bg-card/80 border-border'
                    } border-2`}
                  >
                    <div className="p-5">
                      <p className="whitespace-pre-wrap leading-relaxed text-sm">
                        {message.content}
                      </p>
                      {message.sources && (
                        <div className="mt-4 pt-4 border-t border-border">
                          <div className="flex items-center gap-2 mb-2">
                            <FiFileText size={14} className="text-muted-foreground" />
                            <span className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                              Source References
                            </span>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            {message.sources.map((source) => (
                              <div
                                key={source.id}
                                className="text-xs p-2 bg-background/50 border border-border font-mono"
                              >
                                [{source.id}] {source.title}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[85%]">
                <div className="mb-2">
                  <Badge variant="secondary" className="text-xs font-mono">
                    PROCESSING
                  </Badge>
                </div>
                <Card className="bg-card/80 border-2 border-border">
                  <div className="p-5">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary animate-bounce" />
                      <div className="w-2 h-2 bg-primary animate-bounce" style={{ animationDelay: '0.2s' }} />
                      <div className="w-2 h-2 bg-primary animate-bounce" style={{ animationDelay: '0.4s' }} />
                      <span className="text-xs text-muted-foreground ml-2">Retrieving relevant information...</span>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t-2 border-border bg-card">
        <div className="max-w-5xl mx-auto p-6">
          <div className="flex gap-3">
            <Button variant="outline" size="icon" className="shrink-0 border-2">
              <FiPaperclip size={18} />
            </Button>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter your query here..."
              className="min-h-[70px] resize-none bg-background/50 border-2 font-mono text-sm"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              size="icon"
              className="shrink-0 border-2"
            >
              <FiSend size={18} />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-3 font-mono">
            ENTER to submit • SHIFT+ENTER for new line
          </p>
        </div>
      </div>
    </div>
  );
}
