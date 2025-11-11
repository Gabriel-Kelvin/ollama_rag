import React from 'react';
import { clsx } from 'clsx';

export const Spinner: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={clsx('flex items-center justify-center', className)}>
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );
};

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div
      className={clsx('animate-pulse rounded-md bg-dark', className)}
    />
  );
};

export const PageLoader: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Spinner className="mb-4" />
        <p className="text-gray-400">Loading...</p>
      </div>
    </div>
  );
};

