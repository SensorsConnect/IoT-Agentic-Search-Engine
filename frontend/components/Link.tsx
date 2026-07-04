import { ComponentProps } from 'react'
import { Link as RadixLink } from '@radix-ui/themes'
import NextLink from 'next/link'

type LinkOwnProps = ComponentProps<typeof RadixLink>

interface LinkProps {
  href: string
  className?: string
  color?: LinkOwnProps['color']
  children?: React.ReactNode
  disabled?: boolean
  highContrast?: boolean
}

export const Link = ({ href, className, children, color, highContrast, disabled }: LinkProps) => {
  return (
    <RadixLink
      asChild
      className={className}
      color={color}
      aria-disabled={disabled}
      highContrast={highContrast}
    >
      <NextLink href={href}>{children}</NextLink>
    </RadixLink>
  )
}

export default Link
