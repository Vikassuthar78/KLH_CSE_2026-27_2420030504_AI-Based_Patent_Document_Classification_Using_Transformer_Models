import React, { useState } from 'react';
import { Brain, Sparkles, CheckCircle2, ShieldAlert, ArrowRight, BarChart2 } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { FeatureImportance } from '../charts/FeatureImportance';
import { api } from '../api/client';

export function ExplainabilityLab() {
  const [text, setText] = useState(
    '1. A method of encoding digital media data comprising applying a discrete cosine transform to blocks of the digital media data to produce transform coefficients and quantizing the coefficients.'
  );
  const [targetCode, setTargetCode] = useState('H04N');
  const [loading, setLoading] = useState(false);
  const [faithLoading, setFaithLoading] = useState(false);
  const [explanation, setExplanation] = useState<any>(null);
  const [faithfulness, setFaithfulness] = useState<any>(null);

  async function handleExplain() {
    if (!text.trim()) return;
    setLoading(true);
    setFaithfulness(null);
    try {
      const res = await api.post('/explainability/explain', {
        text,
        target_class_code: targetCode,
        top_k: 12,
      });
      setExplanation(res.data);
    } catch (err) {
      console.error('Explanation failed:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFaithfulness() {
    if (!text.trim()) return;
    setFaithLoading(true);
    try {
      const res = await api.post('/explainability/faithfulness', {
        text,
        target_class_code: targetCode,
        top_k: 12,
      });
      setFaithfulness(res.data);
    } catch (err) {
      console.error('Faithfulness evaluation failed:', err);
    } finally {
      setFaithLoading(false);
    }
  }

  const featuresRecord: Record<string, number> = {};
  if (explanation?.tokens && explanation?.scores) {
    explanation.tokens.forEach((t: string, idx: number) => {
      featuresRecord[t] = explanation.scores[idx];
    });
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Explainability Laboratory</h1>
        <p className="mt-1 text-sm text-slate-500">
          Token-level attribution, feature coefficients, and perturbation-based faithfulness evaluations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="Input Patent Text & Target CPC Class">
            <div className="space-y-4">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={6}
                className="w-full rounded-lg border border-slate-300 p-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-slate-700">Target CPC:</span>
                  <input
                    type="text"
                    value={targetCode}
                    onChange={(e) => setTargetCode(e.target.value.toUpperCase())}
                    className="w-24 px-2.5 py-1.5 border border-slate-300 rounded text-xs font-mono font-semibold"
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleExplain} disabled={loading || !text.trim()}>
                    {loading ? <LoadingSpinner size="sm" /> : <Brain className="w-4 h-4 mr-2" />}
                    Explain Prediction
                  </Button>
                  {explanation && (
                    <Button variant="secondary" onClick={handleFaithfulness} disabled={faithLoading}>
                      {faithLoading ? <LoadingSpinner size="sm" /> : <ShieldAlert className="w-4 h-4 mr-2" />}
                      Test Faithfulness
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </Card>

          {/* Token Attribution Highlighting */}
          {explanation && (
            <Card title="Token Attribution & Evidence Highlighting">
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm leading-relaxed">
                  {text.split(/\s+/).map((word, idx) => {
                    const clean = word.toLowerCase().replace(/[^a-z0-9]/g, '');
                    const tokenIdx = explanation.tokens.findIndex((t: string) => t.toLowerCase() === clean);
                    const score = tokenIdx >= 0 ? explanation.scores[tokenIdx] : 0;
                    let bg = '';
                    if (score > 0.1) bg = 'bg-emerald-100 text-emerald-900 font-semibold px-1 rounded';
                    else if (score > 0.02) bg = 'bg-emerald-50 text-emerald-800 px-0.5 rounded';
                    else if (score < -0.05) bg = 'bg-rose-100 text-rose-900 font-semibold px-1 rounded';

                    return (
                      <span key={idx} className={`inline-block mr-1.5 ${bg}`} title={score !== 0 ? `Attribution: ${score.toFixed(3)}` : ''}>
                        {word}
                      </span>
                    );
                  })}
                </div>
                <div className="flex items-center gap-6 text-xs text-slate-500">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded bg-emerald-200 inline-block" />
                    <span>Positive evidence for {targetCode}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded bg-rose-200 inline-block" />
                    <span>Negative evidence against {targetCode}</span>
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Right Column: Faithfulness & Feature Importance */}
        <div className="space-y-6">
          <Card title="Top Feature Attributions">
            {Object.keys(featuresRecord).length > 0 ? (
              <FeatureImportance features={featuresRecord} />
            ) : (
              <div className="py-16 text-center text-sm text-slate-400">
                Run explanation to view top tokens.
              </div>
            )}
          </Card>

          {faithfulness && (
            <Card title="Faithfulness Evaluation">
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded text-xs">
                  <span className="text-slate-600">Comprehensiveness:</span>
                  <span className="font-mono font-bold text-slate-900">
                    +{faithfulness.comprehensiveness}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded text-xs">
                  <span className="text-slate-600">Sufficiency:</span>
                  <span className="font-mono font-bold text-slate-900">
                    {faithfulness.sufficiency}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 leading-normal">
                  High comprehensiveness proves removing key tokens significantly lowers prediction confidence.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
