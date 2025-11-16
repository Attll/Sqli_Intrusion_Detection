import React from 'react'
import { cn } from '../../utils/helpers'

const Badge = ({ children, variant = 'info', className }) => {
  const variants = {
    success: 'badge-success',
    danger: 'badge-danger',
    warning: 'badge-warning',
    info: 'badge-info',
  }

  return (
    <span className={cn(variants[variant], className)}>
      {children}
    </span>
  )
}

export default Badge
