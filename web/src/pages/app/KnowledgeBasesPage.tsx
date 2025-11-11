import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Loader';
import { Plus, Trash2, Database } from 'lucide-react';
import { api, KnowledgeBase } from '../../lib/api';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';

export const KnowledgeBasesPage: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKbName, setNewKbName] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchKbs = async () => {
    try {
      const response = await api.getKnowledgeBases();
      setKbs(response.data);
    } catch (error) {
      toast.error('Failed to load knowledge bases');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKbs();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKbName.trim()) return;

    setCreating(true);
    try {
      await api.createKnowledgeBase(newKbName);
      toast.success('Knowledge base created successfully');
      setNewKbName('');
      setShowCreateModal(false);
      fetchKbs();
    } catch (error) {
      toast.error('Failed to create knowledge base');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This will also delete all documents and indexed data.`)) return;

    try {
      await api.deleteKnowledgeBase(name);
      toast.success('Knowledge base deleted successfully');
      
      // Immediately remove from local state
      setKbs((prevKbs) => prevKbs.filter((kb) => kb.name !== name));
      
      // Then refresh from server to ensure consistency
      setTimeout(() => {
        fetchKbs();
      }, 500);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to delete knowledge base';
      toast.error(errorMsg);
      console.error('Delete error:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">Knowledge Bases</h1>
          <p className="text-gray-400 mt-1">Manage your document collections</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create New
        </Button>
      </div>

      {kbs.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Database className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-300 mb-2">No Knowledge Bases Yet</h3>
            <p className="text-gray-400 mb-6">Create your first knowledge base to get started</p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Knowledge Base
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {kbs.map((kb) => (
            <motion.div
              key={kb.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <Card>
                <CardContent>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-100 mb-1">{kb.name}</h3>
                      {kb.created_at && (
                        <p className="text-sm text-gray-400">
                          Created {new Date(kb.created_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(kb.name)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary">
                      {kb.doc_count || 0} {kb.doc_count === 1 ? 'document' : 'documents'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-md"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Create Knowledge Base</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleCreate} className="space-y-4">
                    <Input
                      label="Name"
                      placeholder="e.g., Company Docs"
                      value={newKbName}
                      onChange={(e) => setNewKbName(e.target.value)}
                      required
                      autoFocus
                    />
                    <div className="flex space-x-3">
                      <Button type="submit" isLoading={creating} className="flex-1">
                        Create
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setShowCreateModal(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

