import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  Info,
  Activity,
  Database,
  Cpu
} from 'lucide-react';

const API_BASE = "/api";

const FEATURE_NAMES = [
  "mean radius", "mean texture", "mean perimeter", "mean area",
  "mean smoothness", "mean compactness", "mean concavity",
  "mean concave points", "mean symmetry", "mean fractal dimension",
  "radius error", "texture error", "perimeter error", "area error",
  "smoothness error", "compactness error", "concavity error",
  "concave points error", "symmetry error", "fractal dimension error",
  "worst radius", "worst texture", "worst perimeter", "worst area",
  "worst smoothness", "worst compactness", "worst concavity",
  "worst concave points", "worst symmetry", "worst fractal dimension"
];

const DEFAULT_VALS = FEATURE_NAMES.reduce((acc, name) => {
  acc[name] = 15.0;
  return acc;
}, {});

export default function App() {
  const [features, setFeatures] = useState(DEFAULT_VALS);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInput = (name, val) => {
    setFeatures(prev => ({ ...prev, [name]: parseFloat(val) || 0 }));
  };

  const assessPrediction = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features })
      });
      const data = await resp.json();
      console.log("Trust Analysis Received:", data);
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Failed to connect to TRUSTSCOPE backend.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (label) => {
    const l = label?.toUpperCase();
    if (l === 'SAFE') return '#10b981';
    if (l === 'REVIEW') return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="logo">TRUSTSCOPE</div>
        <div className="nav-info">
          <Database size={16} style={{ marginRight: '8px' }} />
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>v1.0.0-Pilot (Medical Trial)</span>
        </div>
      </header>

      <div className="layout-grid">
        <div className="card">
          <div className="card-title">Feature Configuration</div>
          <div className="input-section">
            <div className="feature-grid">
              {FEATURE_NAMES.slice(0, 10).map(name => (
                <div key={name} className="feature-input">
                  <label>{name}</label>
                  <input
                    type="number"
                    step="0.1"
                    value={features[name]}
                    onChange={(e) => handleInput(name, e.target.value)}
                  />
                </div>
              ))}
            </div>
            <button
              className="btn-primary"
              onClick={assessPrediction}
              disabled={loading}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              {loading ? (
                <>
                  <Cpu className="spin" size={18} />
                  Analyzing...
                </>
              ) : "Run Trust Assessment"}
            </button>
          </div>
        </div>

        <div className="result-section">
          {!result ? (
            <div className="card" style={{ height: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#64748b', textAlign: 'center' }}>
              <Activity size={48} style={{ marginBottom: '16px', opacity: 0.2 }} />
              <p>Configure features and run assessment to view trust analytics.</p>
            </div>
          ) : (
            <>
              <div className="card trust-hero" style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div className="score-gauge" style={{
                  flexShrink: 0,
                  width: '120px',
                  height: '120px',
                  borderRadius: '50%',
                  border: `8px solid ${getScoreColor(result?.trust?.trust_label)}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(255,255,255,0.02)'
                }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: '800' }}>
                    {Math.round(result?.trust?.trust_score || 0)}
                  </div>
                </div>

                <div className="trust-details">
                  <div className={`trust-badge badge-${(result?.trust?.trust_label || 'UNSAFE').toLowerCase()}`}>
                    {result?.trust?.trust_label || 'ERROR'}
                  </div>
                  <h2 className="explanation-text" style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>
                    {result?.explanation || 'No explanation available.'}
                  </h2>
                  <div style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'flex', alignItems: 'start', gap: '8px' }}>
                    <Info size={16} />
                    <span><strong>Recommendation:</strong> {result?.trust?.recommendation || 'Consult system logs.'}</span>
                  </div>
                </div>
              </div>

              <div className="signals-grid">
                <div className="card signal-card">
                  <div className="card-title">Agreement</div>
                  <div className="signal-val" style={{ color: (result?.trust?.component_scores?.agreement || 0) > 0.7 ? '#10b981' : '#f59e0b' }}>
                    {Math.round((result?.trust?.component_scores?.agreement || 0) * 100)}%
                  </div>
                  <div className="signal-desc">Cross-model consistency</div>
                </div>
                <div className="card signal-card">
                  <div className="card-title">Certainty</div>
                  <div className="signal-val" style={{ color: (result?.trust?.component_scores?.uncertainty || 0) > 0.7 ? '#10b981' : '#f59e0b' }}>
                    {Math.round((result?.trust?.component_scores?.uncertainty || 0) * 100)}%
                  </div>
                  <div className="signal-desc">Ensemble confidence level</div>
                </div>
                <div className="card signal-card">
                  <div className="card-title">Similarity</div>
                  <div className="signal-val" style={{ color: (result?.trust?.component_scores?.distribution_similarity || 0) > 0.05 ? '#10b981' : '#ef4444' }}>
                    {Math.round((result?.trust?.component_scores?.distribution_similarity || 0) * 100)}%
                  </div>
                  <div className="signal-desc">Dist. match (p-value)</div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 2s linear infinite; }
      `}</style>
    </div>
  );
}
