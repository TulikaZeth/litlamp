import { useState, useEffect } from 'react'
import NotebookHeader from '../components/NotebookHeader'
import SourcesPanel from '../components/SourcesPanel'
import ChatPanel from '../components/ChatPanel'
import { ragAPI } from '../lib/api'

export default function AppPage() {
  const [sources, setSources] = useState([]);
  const [stats, setStats] = useState(null);
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    // Warn user before refresh/close if documents are uploaded
    const handleBeforeUnload = (e) => {
      if (sources.length > 0) {
        e.preventDefault();
        e.returnValue = 'All uploaded documents will be removed and chat history will be lost. Are you sure you want to leave?';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [sources.length]);

  useEffect(() => {
    // Clear API and data on first page load
    const initializeApp = async () => {
      try {
        // Clear knowledge base first
        await ragAPI.clearKnowledgeBase();
        setSources([]);
        
        // Then check API health
        const health = await ragAPI.healthCheck();
        setIsHealthy(true);
        setStats(health);
      } catch (error) {
        console.error('API initialization failed:', error);
        setIsHealthy(false);
      }
    };

    initializeApp();
    
    // Poll stats every 30 seconds
    const interval = setInterval(async () => {
      try {
        const statsData = await ragAPI.getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleUploadComplete = async (result) => {
    // Update stats after upload
    if (result.documents_in_kb !== undefined) {
      setStats(prev => ({ ...prev, documents_in_kb: result.documents_in_kb }));
    }
  };

  const handleClearAll = async () => {
    try {
      await ragAPI.clearKnowledgeBase();
      setSources([]);
      setStats(null);
      // Trigger re-fetch of stats
      const statsData = await ragAPI.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to clear knowledge base:', error);
      alert(`Failed to clear: ${error.message}`);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-background text-foreground overflow-hidden">
      <NotebookHeader isHealthy={isHealthy} stats={stats} />
      
      <div className="flex flex-1 overflow-hidden">
        <SourcesPanel 
          sources={sources} 
          setSources={setSources}
          onUploadComplete={handleUploadComplete}
          onClearAll={handleClearAll}
        />
        <ChatPanel 
          sources={sources}
          stats={stats}
          onClearChat={handleClearAll}
        />
      </div>
      
      {!isHealthy && (
        <div className="fixed bottom-4 right-4 bg-destructive text-destructive-foreground px-4 py-2 rounded-lg shadow-lg">
          API connection failed. Make sure the backend is running at {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
        </div>
      )}
    </div>
  )
}
