import React, { useState } from 'react';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Eye,
  RefreshCw,
  Trash2,
  Table,
  Sliders,
  FolderOpen,
  Cloud,
  Network,
  BarChart3,
  MapPin,
  Truck,
  Users,
} from 'lucide-react';
import { Dataset } from '../types';
import { api } from '../services/api';

interface DatasetManagementProps {
  datasets: Dataset[];
  onRefresh: () => void;
  onScanDatasets: () => void;
  isScanning: boolean;
}

export const DatasetManagement: React.FC<DatasetManagementProps> = ({
  datasets,
  onRefresh,
  onScanDatasets,
  isScanning,
}) => {
  const [selectedType, setSelectedType] = useState<string>('customer');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [activePreview, setActivePreview] = useState<{
    id: string;
    data: any;
    filename: string;
  } | null>(null);
  const [mappingModal, setMappingModal] = useState<{
    dataset: Dataset;
    schemaCols: string[];
  } | null>(null);
  const [selectedMapping, setSelectedMapping] = useState<Record<string, string>>({});

  const datasetCategories = [
    { id: 'customer', label: '1. Customer & Delivery' },
    { id: 'vehicle', label: '2. Vehicle Fleet' },
    { id: 'location', label: '3. Location / GPS' },
    { id: 'traffic', label: '4. Traffic Volume' },
    { id: 'road', label: '5. Road / Distance Network' },
    { id: 'weather', label: '6. Weather Observations' },
  ];

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('dataset_type', selectedType);
      if (datasetName) formData.append('name', datasetName);

      const res = await api.uploadDataset(formData);
      // Automatically trigger extract, validate, and process
      const datasetId = res.id;
      await api.extractDataset(datasetId);
      await api.validateDataset(datasetId);
      await api.processDataset(datasetId);

      setUploadFile(null);
      setDatasetName('');
      onRefresh();
    } catch (err: any) {
      alert(`Upload/processing error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handlePreview = async (dataset: Dataset) => {
    try {
      const res = await api.getPreview(dataset.id, 20);
      const filename = Object.keys(res.previews || {})[0] || dataset.original_filename;
      setActivePreview({
        id: dataset.id,
        filename,
        data: res.previews[filename] || { columns: [], rows: [] },
      });
    } catch (err: any) {
      alert(`Preview failed: ${err.message}`);
    }
  };

  const handleReprocess = async (id: string) => {
    try {
      await api.extractDataset(id);
      await api.validateDataset(id);
      await api.processDataset(id);
      onRefresh();
    } catch (err: any) {
      alert(`Reprocess failed: ${err.message}`);
    }
  };

  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    if (deletingId) return;
    setDeletingId(id);
    try {
      await api.deleteDataset(id);
      if (activePreview?.id === id) setActivePreview(null);
      await onRefresh();
    } catch (err: any) {
      console.error('Delete failed:', err);
      alert(`Delete failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'weather':
        return <Cloud className="h-4 w-4" />;
      case 'road':
        return <Network className="h-4 w-4" />;
      case 'traffic':
        return <BarChart3 className="h-4 w-4" />;
      case 'location':
        return <MapPin className="h-4 w-4" />;
      case 'vehicle':
        return <Truck className="h-4 w-4" />;
      case 'customer':
        return <Users className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Auto-Scan */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-black/10 dark:border-[#29292E]">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#777777] dark:text-[#71717A] mb-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[#B7FF00]" />
            <span>Data Ingestion & Normalization</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
            Datasets
          </h1>
          <p className="text-xs text-[#777777] dark:text-[#A1A1AA] mt-1 max-w-xl">
            Ingest, extract, validate, map columns, and normalize the 6 logistics datasets safely.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onScanDatasets}
            disabled={isScanning}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#080808] dark:bg-[#B7FF00] hover:bg-[#171717] dark:hover:bg-[#a3e600] text-[#B7FF00] dark:text-black rounded-xl text-xs font-heading font-bold shadow-xs hover:shadow transition-all disabled:opacity-50 cursor-pointer"
            title="Auto-discover and ingest all 6 logistics datasets from workspace"
          >
            <FolderOpen className="h-4 w-4 text-[#B7FF00] dark:text-black" />
            <span>{isScanning ? 'Ingesting Datasets...' : 'Ingest Datasets'}</span>
          </button>
          <button
            onClick={onRefresh}
            className="p-2.5 bg-white dark:bg-[#18181B] border border-black/10 dark:border-[#29292E] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] rounded-xl text-[#080808] dark:text-[#F5F5F7] transition-all cursor-pointer shadow-xs"
            title="Refresh Datasets Table and Schema"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Upload Box */}
      <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7] mb-4">
          Upload Dataset (ZIP, XLSX, CSV, JSON, GraphML)
        </h3>

        <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-[#777777] dark:text-[#A1A1AA] mb-1.5">
              Dataset Category
            </label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs border border-black/10 dark:border-[#29292E] rounded-xl bg-white dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#B7FF00]"
            >
              {datasetCategories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#777777] dark:text-[#A1A1AA] mb-1.5">
              Custom Dataset Name (Optional)
            </label>
            <input
              type="text"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="e.g. NYC Customer Orders 2026"
              className="w-full px-3.5 py-2.5 text-xs border border-black/10 dark:border-[#29292E] rounded-xl bg-white dark:bg-[#17171A] text-[#080808] dark:text-[#F5F5F7] placeholder-[#71717A] focus:outline-none focus:ring-2 focus:ring-[#B7FF00]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#777777] dark:text-[#A1A1AA] mb-1.5">
              Select File (ZIP, XLSX, CSV)
            </label>
            <input
              type="file"
              onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
              className="w-full text-xs text-[#777777] dark:text-[#A1A1AA] file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-black/5 dark:file:bg-[#202024] file:text-[#080808] dark:file:text-white hover:file:bg-black/10 dark:hover:file:bg-[#29292E]"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={!uploadFile || isUploading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#080808] dark:bg-[#18181B] border border-transparent dark:border-[#29292E] hover:border-[#B7FF00]/50 text-[#B7FF00] rounded-xl text-xs font-bold shadow-xs transition-all disabled:opacity-40 cursor-pointer"
            >
              <Upload className="h-4 w-4" />
              <span>{isUploading ? 'Extracting & Processing...' : 'Upload & Process'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Datasets Table */}
      <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-black/5 dark:border-[#29292E] flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7]">
            Registered Datasets ({datasets.length})
          </h3>
          <span className="text-xs text-[#777777] dark:text-[#71717A]">
            Safe sandbox extraction & schema detection
          </span>
        </div>

        {datasets.length === 0 ? (
          <div className="p-8 text-center text-[#777777] dark:text-[#71717A]">
            <FileText className="h-10 w-10 mx-auto mb-2 text-[#777777]/50" />
            <p className="text-sm font-bold text-[#080808] dark:text-white">No datasets loaded yet.</p>
            <p className="text-xs text-[#777777] dark:text-[#A1A1AA] mt-1">
              Click &quot;Ingest Datasets&quot; to auto-discover and load the existing NYC datasets.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-transparent border-b border-black/5 dark:border-[#29292E] text-[#777777] dark:text-[#71717A] uppercase font-bold text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Dataset Name / File</th>
                  <th className="py-3 px-4">Records</th>
                  <th className="py-3 px-4">Missing %</th>
                  <th className="py-3 px-4">Extraction</th>
                  <th className="py-3 px-4">Validation</th>
                  <th className="py-3 px-4">Processing</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/5 dark:divide-[#29292E]/60 font-normal">
                {datasets.map((d) => (
                  <tr key={d.id} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="h-7 w-7 rounded-lg bg-black/5 dark:bg-[#18181B] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#A1A1AA] flex items-center justify-center shrink-0">
                          {getTypeIcon(d.dataset_type)}
                        </div>
                        <span className="font-bold text-[#080808] dark:text-[#F5F5F7] capitalize">
                          {d.dataset_type}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-[#080808] dark:text-[#F5F5F7]">{d.name}</div>
                      <div className="text-[11px] text-[#777777] dark:text-[#71717A] truncate max-w-xs font-mono mt-0.5">
                        {d.original_filename} ({(d.file_size_bytes / 1024).toFixed(1)} KB)
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-[#080808] dark:text-[#F5F5F7] font-mono">
                      {d.record_count ? d.record_count.toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-3.5 px-4 text-[#777777] dark:text-[#A1A1AA] font-mono">
                      {d.missing_value_pct ? `${d.missing_value_pct.toFixed(1)}%` : '0%'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-block px-3 py-0.5 rounded-full text-[11px] font-bold ${
                          d.extraction_status === 'extracted'
                            ? 'bg-[#B7FF00] text-black'
                            : d.extraction_status === 'failed'
                            ? 'bg-red-500/20 text-red-400'
                            : 'bg-black/5 dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                        }`}
                      >
                        {d.extraction_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-block px-3 py-0.5 rounded-full text-[11px] font-bold ${
                          d.validation_status === 'valid'
                            ? 'bg-[#B7FF00] text-black'
                            : d.validation_status === 'invalid'
                            ? 'bg-amber-500/20 text-amber-400'
                            : 'bg-black/5 dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                        }`}
                      >
                        {d.validation_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-block px-3 py-0.5 rounded-full text-[11px] font-bold ${
                          d.processing_status === 'completed'
                            ? 'bg-[#B7FF00] text-black'
                            : d.processing_status === 'failed'
                            ? 'bg-red-500/20 text-red-400'
                            : 'bg-black/5 dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                        }`}
                      >
                        {d.processing_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-1.5">
                      <button
                        onClick={() => handlePreview(d)}
                        className="p-1.5 hover:bg-black/5 dark:hover:bg-white/10 text-[#777777] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white rounded-lg transition-all cursor-pointer"
                        title="Preview Records"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleReprocess(d.id)}
                        className="p-1.5 hover:bg-black/5 dark:hover:bg-white/10 text-[#777777] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white rounded-lg transition-all cursor-pointer"
                        title="Reprocess"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(d.id);
                        }}
                        disabled={deletingId === d.id}
                        className="p-1.5 hover:bg-red-50 dark:hover:bg-red-500/10 text-[#777777] hover:text-red-600 dark:hover:text-red-400 rounded-lg transition-all cursor-pointer disabled:opacity-50"
                        title="Delete dataset"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Row Preview Panel */}
      {activePreview && (
        <div className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Table className="h-4 w-4 text-[#B7FF00]" />
              <h3 className="text-sm font-bold text-[#080808] dark:text-[#F5F5F7]">
                Data Preview: {activePreview.filename} (First 20 Records)
              </h3>
            </div>
            <button
              onClick={() => setActivePreview(null)}
              className="text-xs text-[#777777] dark:text-[#A1A1AA] hover:text-black dark:hover:text-white cursor-pointer font-bold"
            >
              Close Preview
            </button>
          </div>

          {activePreview.data.rows && activePreview.data.rows.length > 0 ? (
            <div className="overflow-x-auto max-h-80 border border-black/10 dark:border-[#29292E] rounded-xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-black/[0.03] dark:bg-[#17171A] border-b border-black/10 dark:border-[#29292E] text-[#777777] dark:text-[#A1A1AA] sticky top-0">
                  <tr>
                    {activePreview.data.columns.map((c: string) => (
                      <th key={c} className="py-2 px-3 text-[11px] font-bold whitespace-nowrap">
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-black/5 dark:divide-[#29292E]/60 text-[#171717] dark:text-[#F5F5F7]">
                  {activePreview.data.rows.map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02]">
                      {activePreview.data.columns.map((c: string) => (
                        <td key={c} className="py-2 px-3 whitespace-nowrap text-[11px] font-mono">
                          {String(row[c] !== undefined && row[c] !== null ? row[c] : '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-xs text-[#777777] dark:text-[#A1A1AA]">No tabular preview available for this file.</p>
          )}
        </div>
      )}
    </div>
  );
};
