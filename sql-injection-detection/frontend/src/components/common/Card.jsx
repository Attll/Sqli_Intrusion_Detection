import React from 'react'
import { cn } from '../../utils/helpers'

const Card = ({ children, className, ...props }) => {
  return (
    <div className={cn('card', className)} {...props}>
      {children}
    </div>
  )
}

export default Card
