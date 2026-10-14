import axios from 'axios';
import { Dataset, AnalyticsSummary, OptimizationResponse } from '../types';

// In production, configure VITE_API_URL (e.g. https://routeiq-backend.onrender.com)
// In local dev, defaults to '/api' which is proxied by Vite to http://127.0.0.1:8000
const envApiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '';
const API_BASE = envApiUrl
  ? (envApiUrl.endsWith('/api') ? envApiUrl : `${envApiUrl.replace(/\/$/, '')}/api`)
  : '/api';

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
