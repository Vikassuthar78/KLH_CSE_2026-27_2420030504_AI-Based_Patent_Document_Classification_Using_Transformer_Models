import React, { useRef, useState, useCallback } from 'react';
import { Upload, File, X } from 'lucide-react';
import clsx from 'clsx';

interface FileUploadProps {
  accept?: string;
  onFile: (file: File) => void;
  label?: string;
  description?: string;
  className?: string;
}

export function FileUpload({
  accept = '.txt,.csv,.json',
  onFile,
  label = 'Upload file',
  description = 'Drag and drop or click to browse',
  className,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      setSelectedFile(file);
      onFile(file);
    },
    [onFile]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div className={className}>
      <div
        className={clsx(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          dragOver
            ? 'border-indigo-400 bg-indigo-50'
            : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
        )}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <Upload className="w-8 h-8 text-slate-400 mx-auto mb-3" />
        <p className="text-sm font-medium text-slate-700">{label}</p>
        <p className="text-xs text-slate-500 mt-1">{description}</p>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
        />
      </div>
      {selectedFile && (
        <div className="flex items-center gap-2 mt-3 px-3 py-2 bg-slate-50 rounded-lg">
          <File className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-700 flex-1 truncate">{selectedFile.name}</span>
          <span className="text-xs text-slate-500">
            {(selectedFile.size / 1024).toFixed(1)} KB
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedFile(null);
            }}
            className="p-1 hover:bg-slate-200 rounded"
          >
            <X className="w-3.5 h-3.5 text-slate-400" />
          </button>
        </div>
      )}
    </div>
  );
}
