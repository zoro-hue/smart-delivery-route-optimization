import axios from 'axios';
import { Dataset, AnalyticsSummary, OptimizationResponse } from '../types';

// In production, configure VITE_API_URL (e.g. https://route-iq-backend.onrender.com)
// In staging/preview, configure VITE_STAGING_API_URL (e.g. https://routeiq-backend-staging.onrender.com)
// In local dev, defaults to '/api' which is proxied by Vite to http://127.0.0.1:8000
const PRODUCTION_BACKEND_URL = 'https://route-iq-backend.onrender.com';
const STAGING_BACKEND_URL = 'https://routeiq-backend-staging.onrender.com';

const isBrowser = typeof window !== 'undefined';
const isLocalhost =
  isBrowser &&
  (window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '0.0.0.0');

// A Vercel preview domain has the form: route-iq-frontend-*-projects.vercel.app or contains -git-
// The canonical production domain is: route-iq-frontend-nine.vercel.app
const isVercelPreview =
  isBrowser &&
  window.location.hostname.endsWith('.vercel.app') &&
  !window.location.hostname.startsWith('route-iq-frontend-nine');

const explicitStagingUrl = import.meta.env.VITE_STAGING_API_URL;
const rawApiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;

function resolveApiBase(): string {
  // 1. Local development uses Vite proxy to local backend
  if (isLocalhost) {
    return '/api';
  }

  // 2. Vercel Preview Deployments: Route strictly to isolated staging backend
  if (isVercelPreview) {
    let target = explicitStagingUrl;
    if (!target && rawApiUrl && !rawApiUrl.includes('route-iq-backend.onrender.com') && !rawApiUrl.includes('routeiq-backend.onrender.com')) {
      target = rawApiUrl;
    }
    if (!target) {
      target = STAGING_BACKEND_URL;
    }
    console.info(
      `[ROUTE/IQ Preview Routing] Active preview domain (${window.location.hostname}). Directing API traffic to isolated staging backend: ${target}`
    );
    return target.endsWith('/api') ? target : `${target.replace(/\/$/, '')}/api`;
  }

  // 3. Production Deployments (route-iq-frontend-nine.vercel.app): Route to production backend
  const targetProd = rawApiUrl || PRODUCTION_BACKEND_URL;
  return targetProd.endsWith('/api') ? targetProd : `${targetProd.replace(/\/$/, '')}/api`;
}

const API_BASE = resolveApiBase();

const http = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

// Helper for critical read requests with exponential backoff and preview-to-production fallback
async function requestWithRetry<T>(
  requestFn: () => Promise<T>,
  options: {
    retries?: number;
    delayMs?: number;
    fallbackFn?: () => Promise<T>;
  } = {}
): Promise<T> {
  const retries = options.retries ?? 3;
  let delay = options.delayMs ?? 1000;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await requestFn();
    } catch (err: any) {
      if (attempt === retries) {
        if (options.fallbackFn) {
          console.warn('[ROUTE/IQ API] Primary request failed after retries, invoking fallback backend...', err.message);
          try {
            return await options.fallbackFn();
          } catch (fallbackErr: any) {
            console.error('[ROUTE/IQ API] Fallback backend also failed:', fallbackErr);
            throw err;
          }
        }
        throw err;
      }
      console.warn(`[ROUTE/IQ API] Request attempt ${attempt + 1}/${retries + 1} failed (${err.message}). Retrying in ${delay}ms...`);
      await new Promise((resolve) => setTimeout(resolve, delay));
      delay = Math.min(delay * 1.5, 4000);
    }
  }
  return await requestFn();
}

export const api = {
  // Health
  checkHealth: async () => {
    return requestWithRetry(
      async () => {
        const res = await http.get('/health', { timeout: 15000 });
        return res.data;
      },
      {
        retries: 2,
        delayMs: 1000,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/health`, { timeout: 15000 });
              return fallbackRes.data;
            }
          : undefined,
      }
    );
  },

  // Datasets
  getDatasets: async (signal?: AbortSignal): Promise<Dataset[]> => {
    return requestWithRetry(
      async () => {
        const res = await http.get('/datasets', { timeout: 15000, signal });
        if (!Array.isArray(res.data)) {
          throw new Error(
            typeof res.data === 'string' && res.data.includes('<!doctype')
              ? 'Backend endpoint returned HTML. Please verify deployment routing.'
              : 'Invalid response format from datasets endpoint'
          );
        }
        return res.data;
      },
      {
        retries: 2,
        delayMs: 800,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/datasets`, { timeout: 15000, signal });
              if (Array.isArray(fallbackRes.data)) return fallbackRes.data;
              throw new Error('Invalid response from fallback production endpoint');
            }
          : undefined,
      }
    );
  },

  getDatasetsSummary: async () => {
    const res = await http.get('/datasets/summary', { timeout: 10000 });
    return res.data;
  },

  getDatasetStatus: async (datasetId: string, signal?: AbortSignal) => {
    const res = await http.get(`/datasets/${datasetId}/status`, { timeout: 10000, signal });
    return res.data;
  },

  processDatasetAsync: async (datasetId: string) => {
    const res = await http.post(`/datasets/${datasetId}/process-async`, {}, { timeout: 15000 });
    return res.data;
  },

  getDatasetJobStatus: async (jobId: string, signal?: AbortSignal) => {
    const res = await http.get(`/datasets/jobs/${jobId}`, { timeout: 10000, signal });
    return res.data;
  },

  scanWorkspace: async () => {
    const res = await http.post('/datasets/scan-workspace');
    return res.data;
  },

  uploadDataset: async (formData: FormData) => {
    const res = await http.post('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  extractDataset: async (datasetId: string) => {
    const res = await http.post(`/datasets/${datasetId}/extract`);
    return res.data;
  },

  validateDataset: async (datasetId: string) => {
    const res = await http.post(`/datasets/${datasetId}/validate`);
    return res.data;
  },

  mapColumns: async (datasetId: string, mapping: Record<string, string>) => {
    const res = await http.post(`/datasets/${datasetId}/map-columns`, mapping);
    return res.data;
  },

  processDataset: async (datasetId: string) => {
    const res = await http.post(`/datasets/${datasetId}/process`);
    return res.data;
  },

  reprocessDataset: async (datasetId: string) => {
    try {
      const res = await http.post(`/datasets/${datasetId}/reprocess`);
      return res.data;
    } catch {
      try {
        await http.post(`/datasets/${datasetId}/extract`);
      } catch {}
      await http.post(`/datasets/${datasetId}/validate`);
      const proc = await http.post(`/datasets/${datasetId}/process`);
      return proc.data;
    }
  },

  getPreview: async (datasetId: string, rows = 20) => {
    return requestWithRetry(
      async () => {
        const res = await http.get(`/datasets/${datasetId}/preview?rows=${rows}`, { timeout: 25000 });
        return res.data;
      },
      {
        retries: 2,
        delayMs: 1000,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/datasets/${datasetId}/preview?rows=${rows}`, { timeout: 25000 });
              return fallbackRes.data;
            }
          : undefined,
      }
    );
  },

  deleteDataset: async (datasetId: string) => {
    const res = await http.delete(`/datasets/${datasetId}`);
    return res.data;
  },

  // Analytics & Road Network
  getAnalyticsSummary: async (): Promise<AnalyticsSummary> => {
    return requestWithRetry(
      async () => {
        const res = await http.get('/analytics/summary', { timeout: 25000 });
        return res.data;
      },
      {
        retries: 2,
        delayMs: 1000,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/analytics/summary`, { timeout: 25000 });
              return fallbackRes.data;
            }
          : undefined,
      }
    );
  },

  getRoadNetwork: async () => {
    return requestWithRetry(
      async () => {
        const res = await http.get('/road-network', { timeout: 25000 });
        return res.data;
      },
      {
        retries: 2,
        delayMs: 1000,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/road-network`, { timeout: 25000 });
              return fallbackRes.data;
            }
          : undefined,
      }
    );
  },

  // Optimization
  getDeliveryStops: async (limit = 50) => {
    return requestWithRetry(
      async () => {
        const res = await http.get(`/delivery-stops?limit=${limit}`, { timeout: 25000 });
        return res.data;
      },
      {
        retries: 2,
        delayMs: 1000,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/delivery-stops?limit=${limit}`, { timeout: 25000 });
              return fallbackRes.data;
            }
          : undefined,
      }
    );
  },

  estimateProblemSize: async (params: any) => {
    const res = await http.post('/optimization/estimate', params);
    return res.data;
  },

  getAlgorithms: async () => {
    return requestWithRetry(
      async () => {
        const res = await http.get('/optimization/algorithms', { timeout: 25000 });
        return res.data;
      },
      {
        retries: 2,
        delayMs: 1000,
        fallbackFn: (isVercelPreview && !rawApiUrl)
          ? async () => {
              const fallbackRes = await axios.get(`${PRODUCTION_BACKEND_URL}/api/optimization/algorithms`, { timeout: 25000 });
              return fallbackRes.data;
            }
          : undefined,
      }
    );
  },

  runOptimization: async (params: any, signal?: AbortSignal): Promise<OptimizationResponse> => {
    const res = await http.post('/optimization/run', params, { signal });
    return res.data;
  },

  // Asynchronous Background Optimization Job Lifecycle
  startOptimizationJob: async (params: any, signal?: AbortSignal): Promise<any> => {
    const res = await http.post('/optimization/jobs', params, { signal });
    return res.data;
  },

  getJobStatus: async (jobId: string, signal?: AbortSignal, maxRetries = 4): Promise<any> => {
    let attempt = 0;
    while (attempt <= maxRetries) {
      try {
        const res = await http.get(`/optimization/jobs/${jobId}/status`, { signal, timeout: 25000 });
        return res.data;
      } catch (err: any) {
        attempt++;
        if (attempt > maxRetries || axios.isCancel(err) || signal?.aborted) {
          throw err;
        }
        await new Promise((r) => setTimeout(r, Math.min(attempt * 800, 2500)));
      }
    }
  },

  cancelOptimizationJob: async (jobId: string): Promise<any> => {
    const res = await http.post(`/optimization/jobs/${jobId}/cancel`);
    return res.data;
  },

  // Experiments
  getExperiments: async (page = 1, size = 20) => {
    const res = await http.get(`/experiments?page=${page}&size=${size}`);
    return res.data;
  },

  getExperimentDetails: async (experimentId: string) => {
    const res = await http.get(`/experiments/${experimentId}`);
    return res.data;
  },

  deleteExperiment: async (experimentId: string) => {
    const res = await http.delete(`/experiments/${experimentId}`);
    return res.data;
  },
};
