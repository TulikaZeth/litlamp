const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const ragAPI = {
  // Main RAG endpoint - handles upload and/or query
  async query(formData) {
    const response = await fetch(`${API_BASE_URL}/api/rag`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to process request');
    }

    return response.json();
  },

  // Upload documents only
  async uploadDocuments(files, useOcr = true, clearKb = false) {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    formData.append('use_ocr', useOcr.toString());
    formData.append('clear_kb', clearKb.toString());

    return this.query(formData);
  },

  // Ask question about existing documents
  async askQuestion(question) {
    const formData = new FormData();
    formData.append('question', question);

    return this.query(formData);
  },

  // Upload and ask in one call
  async uploadAndAsk(files, question, useOcr = true) {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    formData.append('question', question);
    formData.append('use_ocr', useOcr.toString());

    return this.query(formData);
  },

  // Health check
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.json();
  },

  // Get statistics
  async getStats() {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    return response.json();
  },

  // Clear knowledge base
  async clearKnowledgeBase() {
    const response = await fetch(`${API_BASE_URL}/api/clear`, {
      method: 'DELETE',
    });
    return response.json();
  },
};
