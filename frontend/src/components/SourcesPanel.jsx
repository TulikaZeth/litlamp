import { Plus, Search, Check, X, Upload, FileText, MessageSquarePlus } from 'lucide-react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { useState, useRef } from 'react';
import { ragAPI } from '../lib/api';

export default function SourcesPanel({ sources, setSources, onUploadComplete, onClearAll }) {
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const fileInputRef = useRef(null);

  const handleNewChat = async () => {
    setClearing(true);
    setShowConfirmDialog(false);
    try {
      if (onClearAll) {
        await onClearAll();
      }
    } finally {
      setClearing(false);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      const result = await ragAPI.uploadDocuments(Array.from(files), true, false);
      
      // Add uploaded files to sources list
      const newSources = Array.from(files).map((file, idx) => ({
        id: Date.now() + idx,
        name: file.name,
        selected: true,
        type: file.type,
        size: file.size
      }));
      
      setSources([...sources, ...newSources]);
      
      if (onUploadComplete) {
        onUploadComplete(result);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const toggleSourceSelection = (id) => {
    setSources(sources.map(source => 
      source.id === id ? { ...source, selected: !source.selected } : source
    ));
  };

  const removeSource = (id) => {
    setSources(sources.filter(source => source.id !== id));
  };

  return (
    <div className="hidden md:flex md:w-64 lg:w-80 bg-card border-r border-border flex-col h-full relative">
      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="bg-card border-2 border-border rounded-lg shadow-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2">Clear All Data?</h3>
            <p className="text-sm text-muted-foreground mb-6">
              This will clear all uploaded documents and chat history. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => setShowConfirmDialog(false)}
                disabled={clearing}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleNewChat}
                disabled={clearing}
                className="gap-2"
              >
                {clearing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Clearing...
                  </>
                ) : (
                  'Clear All'
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-3 md:p-4 border-b border-border">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <h2 className="text-base md:text-lg font-semibold">Sources</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowConfirmDialog(true)}
              disabled={clearing || sources.length === 0}
              className="gap-1 md:gap-2 text-xs cursor-pointer px-2 md:px-3"
            >
              {clearing ? (
                <>
                  <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  Clearing...
                </>
              ) : (
                <>
                  <MessageSquarePlus size={14} />
                  New Chat
                </>
              )}
            </Button>
          </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.txt,.md,.docx"
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
        />
        <Button 
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full justify-start gap-2 bg-background hover:bg-accent text-foreground border border-border text-sm"
        >
          {uploading ? (
            <>
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Plus size={16} />
              Add sources
            </>
          )}
        </Button>
      </div>

      {/* Search */}
      <div className="px-3 md:px-4 pb-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
          <Input
            placeholder="Search sources"
            className="pl-9 bg-background border-border"
          />
        </div>
      </div>

      {/* Sources List */}
      <ScrollArea className="flex-1">
        <div className="px-3 md:px-4">
          {sources.length > 0 && (
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">
                {sources.length} source{sources.length !== 1 ? 's' : ''}
              </span>
            </div>
          )}
          
          {sources.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Upload size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No sources yet</p>
              <p className="text-xs mt-1">Upload documents to get started</p>
            </div>
          ) : (
            sources.map((source) => (
              <Card
                key={source.id}
                className={`mb-2 p-3 transition-colors ${
                  source.selected ? 'bg-primary/20 border-primary' : 'bg-background hover:bg-accent'
                }`}
              >
                <div className="flex items-start gap-2">
                  <div 
                    className="text-blue-400 mt-1 cursor-pointer"
                    onClick={() => toggleSourceSelection(source.id)}
                  >
                    <FileText size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm break-words">{source.name}</p>
                    {source.size && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {(source.size / 1024).toFixed(1)} KB
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    {source.selected && <Check className="text-primary shrink-0" size={16} />}
                    <button
                      onClick={() => removeSource(source.id)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
      </div>
    </div>
  );
}
