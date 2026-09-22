export function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}

export function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function confidenceTone(value) {
  if (value >= 90) return 'ok'
  if (value >= 75) return 'warn'
  return 'danger'
}
