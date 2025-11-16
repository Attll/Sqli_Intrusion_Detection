import React from 'react'
import { cn } from '../../utils/helpers'
import { Loader2 } from 'lucide-react'

const Button = ({ 
  children, 
  variant = 'primary', 
  isLoading = false, 
  disabled = false,
  className,
  ...props 
}) => {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
  }

  return (
    <button
      className={cn(
        variants[variant],
        'flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  )
}

export default Button
