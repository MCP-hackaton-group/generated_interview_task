export function Avatar({ children, className, ...props }) {
  return (
    <div className={`relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full ${className || ""}`} {...props}>
      {children}
    </div>
  )
}
