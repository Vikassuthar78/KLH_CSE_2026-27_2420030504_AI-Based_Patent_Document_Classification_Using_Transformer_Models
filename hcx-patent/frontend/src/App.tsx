import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Overview } from './pages/Overview';
import { DatasetExplorer } from './pages/DatasetExplorer';
import { ClassificationWorkspace } from './pages/ClassificationWorkspace';
import { TaxonomyExplorer } from './pages/TaxonomyExplorer';
import { ExplainabilityLab } from './pages/ExplainabilityLab';
import { UncertaintyLab } from './pages/UncertaintyLab';
import { DriftAnalysis } from './pages/DriftAnalysis';
import { ExperimentCenter } from './pages/ExperimentCenter';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="dataset" element={<DatasetExplorer />} />
          <Route path="classify" element={<ClassificationWorkspace />} />
          <Route path="taxonomy" element={<TaxonomyExplorer />} />
          <Route path="explainability" element={<ExplainabilityLab />} />
          <Route path="uncertainty" element={<UncertaintyLab />} />
          <Route path="drift" element={<DriftAnalysis />} />
          <Route path="experiments" element={<ExperimentCenter />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

