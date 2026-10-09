import type { FC, ReactNode, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  children: ReactNode;
}

export const Button: FC<ButtonProps> = ({ variant = 'primary', children, className = '', ...props }) => {
  const base = 'px-4 py-2 rounded-xl font-semibold transition-all duration-200 cursor-pointer text-xs flex items-center justify-center gap-2 tracking-wide';
  const styles = {
    primary: 'liquid-btn-primary',
    secondary: 'liquid-btn-secondary',
    danger: 'bg-red-500/10 hover:bg-red-500/20 text-red-600 border border-red-500/30 shadow-sm backdrop-blur-md',
  };

  return (
    <button className={`${base} ${styles[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};
