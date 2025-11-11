import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Loader';
import { FileSearch, CheckCircle, FileText } from 'lucide-react';
import { api, KnowledgeBase } from '../../lib/api';
import { toast } from 'react-toastify';

export const IndexPage: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [files, setFiles] = useState<string[]>([]);
  const [indexedDocs, setIndexedDocs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [indexing, setIndexing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

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
    if (selectedKb) {
      fetchFiles();
      fetchIndexedDocs();
    }
  }, [selectedKb]);

  const fetchFiles = async () => {
    if (!selectedKb) return;
    try {
      const response = await api.getUploadedFiles(selectedKb);
      setFiles(response.data.map((f) => f.filename));
    } catch (error) {
      setFiles([]);
    }
  };

  const fetchIndexedDocs = async () => {
    if (!selectedKb) return;
    try {
      const response = await api.getIndexedDocuments(selectedKb);
      setIndexedDocs(response.data.documents || []);
    } catch (error) {
      setIndexedDocs([]);
    }
  };

  const handleIndex = async () => {
    if (!selectedKb || files.length === 0) {
      toast.error('No files to index');
      return;
    }

    setIndexing(true);
    setLogs([]);
    
    setLogs((prev) => [...prev, `Starting indexing for ${files.length} file(s)...`]);

    try {
      await api.indexDocuments(selectedKb, files);
      setLogs((prev) => [...prev, `✓ Successfully indexed ${files.length} file(s)`]);
      toast.success('Documents indexed successfully');
      fetchIndexedDocs();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to index documents';
      setLogs((prev) => [...prev, `✗ Error: ${errorMsg}`]);
      toast.error(errorMsg);
    } finally {
      setIndexing(false);
    }
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
          <p>Please create a knowledge base and upload documents first.</p>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Index Documents</h1>
        <p className="text-gray-400 mt-1">Process and index your documents for search</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select Knowledge Base</CardTitle>
        </CardHeader>
        <CardContent>
          <select
            value={selectedKb}
            onChange={(e) => setSelectedKb(e.target.value)}
            className="input"
          >
            {kbs.map((kb) => (
              <option key={kb.name} value={kb.name}>
                {kb.name}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Documents to Index</CardTitle>
            <Badge variant="secondary">
              {files.length} {files.length === 1 ? 'file' : 'files'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {files.length === 0 ? (
            <Alert variant="info">
              <p>No documents uploaded yet. Please upload files first.</p>
            </Alert>
          ) : (
            <>
              <div className="space-y-2 mb-4">
                {files.map((filename) => {
                  const isIndexed = indexedDocs.includes(filename);
                  return (
                    <div
                      key={filename}
                      className="flex items-center justify-between p-3 bg-dark rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-primary" />
                        <span className="text-sm text-gray-100">{filename}</span>
                      </div>
                      {isIndexed && (
                        <Badge variant="success">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Indexed
                        </Badge>
                      )}
                    </div>
                  );
                })}
              </div>
              <Button onClick={handleIndex} isLoading={indexing} className="w-full">
                <FileSearch className="h-4 w-4 mr-2" />
                {indexing ? 'Indexing...' : 'Index Documents'}
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {logs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Indexing Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-background rounded-lg p-4 font-mono text-sm space-y-1 max-h-64 overflow-y-auto">
              {logs.map((log, index) => (
                <div key={index} className="text-gray-300">
                  {log}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

