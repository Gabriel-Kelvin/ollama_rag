import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';
import { Badge } from '../../components/ui/Badge';
import { Settings as SettingsIcon, Activity, Server } from 'lucide-react';
import { api } from '../../lib/api';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';

export const SettingsPage: React.FC = () => {
  const [checking, setChecking] = useState(false);
  const [healthStatus, setHealthStatus] = useState<{
    status: 'unknown' | 'healthy' | 'error';
    message?: string;
    details?: any;
  }>({ status: 'unknown' });
  const { user } = useAuth();

  const checkHealth = async () => {
    setChecking(true);
    try {
      const response = await api.health();
      setHealthStatus({
        status: 'healthy',
        message: 'Backend is running normally',
        details: response.data,
      });
      toast.success('Health check passed');
    } catch (error: any) {
      setHealthStatus({
        status: 'error',
        message: error.response?.data?.detail || 'Failed to connect to backend',
      });
      toast.error('Health check failed');
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Settings</h1>
        <p className="text-gray-400 mt-1">Manage your application settings</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <SettingsIcon className="h-6 w-6 text-primary" />
            <div>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Your current account details</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-400">Email</label>
              <p className="text-gray-100 mt-1">{user?.email}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-400">User ID</label>
              <p className="text-gray-100 mt-1 font-mono text-sm">{user?.id}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-400">Email Verified</label>
              <div className="mt-1">
                {user?.email_confirmed_at ? (
                  <Badge variant="success">Verified</Badge>
                ) : (
                  <Badge variant="warning">Not Verified</Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <Server className="h-6 w-6 text-primary" />
            <div>
              <CardTitle>Backend Configuration</CardTitle>
              <CardDescription>API endpoints and connection status</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-400">API Base URL</label>
            <p className="text-gray-100 mt-1 font-mono text-sm">
              {import.meta.env.VITE_API_BASE_URL}
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-400">Supabase URL</label>
            <p className="text-gray-100 mt-1 font-mono text-sm">
              {import.meta.env.VITE_SUPABASE_URL}
            </p>
          </div>

          <div className="pt-4 border-t border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Activity className="h-5 w-5 text-primary" />
                <span className="font-medium text-gray-100">Backend Health</span>
              </div>
              <Button onClick={checkHealth} isLoading={checking} size="sm" variant="secondary">
                Check Health
              </Button>
            </div>

            {healthStatus.status !== 'unknown' && (
              <Alert
                variant={healthStatus.status === 'healthy' ? 'success' : 'danger'}
                title={healthStatus.status === 'healthy' ? 'Healthy' : 'Error'}
              >
                <p>{healthStatus.message}</p>
                {healthStatus.details && (
                  <pre className="mt-2 text-xs bg-background/50 rounded p-2 overflow-auto">
                    {JSON.stringify(healthStatus.details, null, 2)}
                  </pre>
                )}
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p className="text-gray-300">
              <strong>Application:</strong> Ollama RAG Demo
            </p>
            <p className="text-gray-300">
              <strong>Version:</strong> 1.0.0
            </p>
            <p className="text-gray-400">
              A modern RAG (Retrieval-Augmented Generation) application with Supabase authentication
              and FastAPI backend.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

