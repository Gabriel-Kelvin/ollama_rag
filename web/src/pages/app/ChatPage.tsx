import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Textarea } from '../../components/ui/Textarea';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Loader';
import { Send, Bot, User as UserIcon, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { api, KnowledgeBase, ChatMessage, RetrievalContext } from '../../lib/api';
import { toast } from 'react-toastify';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

interface MessageWithContext extends ChatMessage {
  contexts?: RetrievalContext[];
}

export const ChatPage: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [messages, setMessages] = useState<MessageWithContext[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [expandedContexts, setExpandedContexts] = useState<number[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchKbs = async () => {
      try {
        const response = await api.getKnowledgeBases();
        setKbs(response.data);
        if (response.data.length > 0) {
          setSelectedKb(response.data[0].name);
        }
      } catch (error) {
        toast.error('Failed to load knowledge bases');
      } finally {
        setLoading(false);
      }
    };
    fetchKbs();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedKb) return;

    const userMessage: MessageWithContext = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setSending(true);

    try {
      const history = messages.map(({ role, content }) => ({ role, content }));
      const response = await api.chat(selectedKb, userMessage.content, history);

      const assistantMessage: MessageWithContext = {
        role: 'assistant',
        content: response.data.response,
        contexts: response.data.contexts,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to get response';
      toast.error(errorMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${errorMsg}`,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleContext = (index: number) => {
    setExpandedContexts((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    );
  }

  if (kbs.length === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <Alert variant="warning" title="No Knowledge Bases">
          <p>Please create a knowledge base and index documents first.</p>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto h-full flex flex-col">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-gray-100">Chat</h1>
        <p className="text-gray-400 mt-1">Ask questions about your documents</p>
      </div>

      <Card className="mb-4">
        <CardContent className="py-4">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-300">Knowledge Base:</label>
            <select
              value={selectedKb}
              onChange={(e) => {
                setSelectedKb(e.target.value);
                setMessages([]);
              }}
              className="input flex-1"
            >
              {kbs.map((kb) => (
                <option key={kb.name} value={kb.name}>
                  {kb.name}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card className="flex-1 flex flex-col min-h-0">
        <CardContent className="flex-1 flex flex-col min-h-0 p-4">
          {messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Bot className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-300 mb-2">Start a Conversation</h3>
                <p className="text-gray-400">Ask me anything about your documents</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-3xl ${
                        message.role === 'user' ? 'bg-secondary' : 'bg-dark border border-primary/30'
                      } rounded-lg p-4`}
                    >
                      <div className="flex items-start space-x-3">
                        <div
                          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                            message.role === 'user' ? 'bg-secondary/50' : 'bg-primary/20'
                          }`}
                        >
                          {message.role === 'user' ? (
                            <UserIcon className="h-5 w-5 text-white" />
                          ) : (
                            <Bot className="h-5 w-5 text-primary" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="prose prose-invert max-w-none text-sm">
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                          </div>

                          {message.contexts && message.contexts.length > 0 && (
                            <div className="mt-4 space-y-2">
                              <button
                                onClick={() => toggleContext(index)}
                                className="flex items-center space-x-2 text-xs text-gray-400 hover:text-gray-300"
                              >
                                <FileText className="h-3 w-3" />
                                <span>
                                  {message.contexts.length} source{message.contexts.length !== 1 && 's'}
                                </span>
                                {expandedContexts.includes(index) ? (
                                  <ChevronUp className="h-3 w-3" />
                                ) : (
                                  <ChevronDown className="h-3 w-3" />
                                )}
                              </button>

                              {expandedContexts.includes(index) && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: 'auto', opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  className="space-y-2"
                                >
                                  {message.contexts.map((ctx, ctxIndex) => (
                                    <div key={ctxIndex} className="bg-background/50 rounded p-3 text-xs">
                                      <div className="flex items-center justify-between mb-2">
                                        <Badge variant="primary" className="text-xs">
                                          {ctx.filename}
                                        </Badge>
                                        {ctx.score && (
                                          <span className="text-gray-500">
                                            Score: {ctx.score.toFixed(2)}
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-gray-300 whitespace-pre-wrap">{ctx.text}</p>
                                    </div>
                                  ))}
                                </motion.div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          )}

          <div className="flex space-x-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask a question..."
              className="resize-none"
              rows={3}
              disabled={sending}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || sending}
              isLoading={sending}
              className="self-end"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

