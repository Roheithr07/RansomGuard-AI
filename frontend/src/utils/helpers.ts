export function getSeverityBadgeColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    case 'high':
      return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    case 'medium':
      return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    default:
      return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  }
}
