import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Loader';
import { Upload as UploadIcon, FileText, Trash2, AlertCircle } from 'lucide-react';
import { api, KnowledgeBase, UploadedFile } from '../../lib/api';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

export const UploadPage: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

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
    }
  }, [selectedKb]);

  const fetchFiles = async () => {
    if (!selectedKb) return;
    try {
      const response = await api.getUploadedFiles(selectedKb);
      setFiles(response.data);
    } catch (error) {
      // Ignore error if no files exist
      setFiles([]);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [selectedKb]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (fileList: FileList) => {
    if (!selectedKb) {
      toast.error('Please select a knowledge base first');
      return;
    }

    const file = fileList[0]; // Handle one file at a time for simplicity
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain',
    ];

    if (!allowedTypes.includes(file.type)) {
      toast.error('Only PDF, DOC, DOCX, and TXT files are supported');
      return;
    }

    setUploading(true);
    try {
      await api.uploadFile(selectedKb, file);
      toast.success(`${file.name} uploaded successfully`);
      fetchFiles();
    } catch (error) {
      toast.error(`Failed to upload ${file.name}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`Delete ${filename}?`)) return;

    try {
      await api.deleteFile(selectedKb, filename);
      toast.success('File deleted');
      fetchFiles();
    } catch (error) {
      toast.error('Failed to delete file');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
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
          <p>Please create a knowledge base first before uploading documents.</p>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Upload Documents</h1>
        <p className="text-gray-400 mt-1">Add files to your knowledge base</p>
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
        <CardContent>
          <form
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive ? 'border-primary bg-primary/5' : 'border-gray-600'
            }`}
          >
            <input
              type="file"
              id="file-upload"
              className="hidden"
              onChange={handleChange}
              accept=".pdf,.doc,.docx,.txt"
              disabled={uploading}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <UploadIcon className="h-12 w-12 text-gray-500 mx-auto mb-4" />
              <p className="text-lg text-gray-300 mb-2">
                {uploading ? 'Uploading...' : 'Drag & drop your file here'}
              </p>
              <p className="text-sm text-gray-500 mb-4">or</p>
              <Button type="button" variant="secondary" disabled={uploading} isLoading={uploading}>
                Browse Files
              </Button>
              <p className="text-xs text-gray-500 mt-4">Supports PDF, DOC, DOCX, TXT</p>
            </label>
          </form>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Files</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {files.map((file) => (
                <motion.div
                  key={file.filename}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-4 bg-dark rounded-lg"
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <FileText className="h-5 w-5 text-primary flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-100 truncate">{file.filename}</p>
                      <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(file.filename)}
                    className="text-red-400 hover:text-red-300 flex-shrink-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

