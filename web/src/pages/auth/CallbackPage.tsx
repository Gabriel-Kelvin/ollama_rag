import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../lib/supabase.ts';
import { PageLoader } from '../../components/ui/Loader';
import { toast } from 'react-toastify';

export const CallbackPage: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const { data, error } = await supabase.auth.getSession();
        
        if (error) throw error;

        if (data.session) {
          toast.success('Email verified successfully!');
          navigate('/app/kb');
        } else {
          toast.error('Failed to verify email');
          navigate('/auth/login');
        }
      } catch (error) {
        console.error('Callback error:', error);
        toast.error('An error occurred during verification');
        navigate('/auth/login');
      }
    };

    handleCallback();
  }, [navigate]);

  return <PageLoader />;
};

