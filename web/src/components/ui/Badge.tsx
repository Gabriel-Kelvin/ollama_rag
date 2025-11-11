import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-gray-700 text-gray-100',
        primary: 'bg-primary/20 text-primary border border-primary/50',
        secondary: 'bg-secondary/20 text-secondary border border-secondary/50',
        success: 'bg-green-900/50 text-green-400 border border-green-700',
        warning: 'bg-yellow-900/50 text-yellow-400 border border-yellow-700',
        danger: 'bg-red-900/50 text-red-400 border border-red-700',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export const Badge: React.FC<BadgeProps> = ({ className, variant, ...props }) => {
  return <div className={clsx(badgeVariants({ variant }), className)} {...props} />;
};

