/**
 * Re-export all API client functions from centralized lib/api.ts
 * and preserve fetchJson backward compatibility.
 */
export * from '../lib/api';
import { apiRequest } from '../lib/api';

export async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  return apiRequest<T>(endpoint, options);
}
