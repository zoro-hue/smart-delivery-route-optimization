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

export const api = {
  // Health
  checkHealth: async () => {
    const res = await http.get('/health');
    return res.data;
  },

  // Datasets
  getDatasets: async (): Promise<Dataset[]> => {
    const res = await http.get('/datasets');
    if (!Array.isArray(res.data)) {
      throw new Error(
        typeof res.data === 'string' && res.data.includes('<!doctype')
          ? 'Backend endpoint returned HTML. Please verify deployment routing.'
          : 'Invalid response format from datasets endpoint'
      );
    }
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
    const res = await http.get(`/datasets/${datasetId}/preview?rows=${rows}`);
    return res.data;
  },

  deleteDataset: async (datasetId: string) => {
    const res = await http.delete(`/datasets/${datasetId}`);
    return res.data;
  },

  // Analytics & Road Network
  getAnalyticsSummary: async (): Promise<AnalyticsSummary> => {
    const res = await http.get('/analytics/summary');
    return res.data;
  },

  getRoadNetwork: async () => {
    const res = await http.get('/road-network');
    return res.data;
  },

  // Optimization
  getDeliveryStops: async (limit = 50) => {
    const res = await http.get(`/delivery-stops?limit=${limit}`);
    return res.data;
  },

  estimateProblemSize: async (params: any) => {
    const res = await http.post('/optimization/estimate', params);
    return res.data;
  },

  getAlgorithms: async () => {
    const res = await http.get('/optimization/algorithms');
    return res.data;
  },

  runOptimization: async (params: any): Promise<OptimizationResponse> => {
    const res = await http.post('/optimization/run', params);
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
