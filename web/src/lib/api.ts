import axios, { AxiosError } from 'axios';
import { supabase } from './supabase.ts';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!apiBaseUrl) {
  throw new Error('Missing API base URL');
}

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

// API Types
export interface KnowledgeBase {
  name: string;
  created_at?: string;
  doc_count?: number;
}

export interface UploadedFile {
  filename: string;
  size: number;
  kb_name?: string;
  upload_date?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface RetrievalContext {
  text: string;
  filename: string;
  score?: number;
}

// API Methods
export const api = {
  // Health check
  health: () => apiClient.get('/health'),

  // Knowledge Bases
  getKnowledgeBases: () => apiClient.get<KnowledgeBase[]>('/knowledge-bases'),
  createKnowledgeBase: (name: string) => apiClient.post('/knowledge-bases', { name }),
  deleteKnowledgeBase: (name: string) => apiClient.delete(`/knowledge-bases/${name}`),

  // Upload
  uploadFile: (kbName: string, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('kb_name', kbName);
    
    return apiClient.post<{ filename: string; message: string }>('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
  },

  getUploadedFiles: (kbName: string) => apiClient.get<UploadedFile[]>(`/uploads/${kbName}`),
  deleteFile: (kbName: string, filename: string) => 
    apiClient.delete(`/uploads/${kbName}/${filename}`),

  // Index
  indexDocuments: (kbName: string, filenames: string[]) => 
    apiClient.post('/index', { kb_name: kbName, filenames }),

  getIndexedDocuments: (kbName: string) => 
    apiClient.get<{ documents: string[] }>(`/indexed/${kbName}`),

  // Retrieve
  retrieve: (kbName: string, query: string, topK?: number) => 
    apiClient.post<{ contexts: RetrievalContext[] }>('/retrieve', {
      kb_name: kbName,
      query,
      top_k: topK || 5,
    }),

  // Chat
  chat: (kbName: string, query: string, history?: ChatMessage[]) => 
    apiClient.post<{ response: string; contexts: RetrievalContext[] }>('/chat', {
      kb_name: kbName,
      query,
      history: history || [],
    }),
};
