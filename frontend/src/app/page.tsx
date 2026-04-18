"use client";

import { useState } from "react";
import { usePredictChurn } from "@/hooks/usePredictChurn";
import { CustomerData } from "@/types/prediction";

const DEFAULT_CUSTOMER: CustomerData = {
  gender: "Female",
  SeniorCitizen: 0,
  Partner: "Yes",
  Dependents: "No",
  tenure: 12,
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "Fiber optic",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: 70.35,
  TotalCharges: "844.2",
};

export default function Home() {
  const [formData, setFormData] = useState<CustomerData>(DEFAULT_CUSTOMER);
  const { predict, loading, error, result, reset } = usePredictChurn();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await predict(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "tenure" || name === "SeniorCitizen" || name === "MonthlyCharges" 
        ? Number(value) 
        : value,
    }));
  };

  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent mb-2">
            ChurnGuardian AI
          </h1>
          <p className="text-gray-400">Advanced Customer Churn Prediction & Analysis</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Form Section */}
          <section className="bg-[#161616] border border-[#262626] rounded-2xl p-8 shadow-xl">
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              Customer Profile
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs uppercase text-gray-500 mb-1">Gender</label>
                  <select 
                    name="gender" 
                    value={formData.gender}
                    onChange={handleChange}
                    className="w-full bg-[#222] border border-[#333] rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs uppercase text-gray-500 mb-1">Tenure (Months)</label>
                  <input 
                    type="number" 
                    name="tenure"
                    value={formData.tenure}
                    onChange={handleChange}
                    className="w-full bg-[#222] border border-[#333] rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs uppercase text-gray-500 mb-1">Internet Service</label>
                <select 
                  name="InternetService" 
                  value={formData.InternetService}
                  onChange={handleChange}
                  className="w-full bg-[#222] border border-[#333] rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="DSL">DSL</option>
                  <option value="Fiber optic">Fiber optic</option>
                  <option value="No">No</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs uppercase text-gray-500 mb-1">Monthly Charges</label>
                  <input 
                    type="number" 
                    name="MonthlyCharges"
                    step="0.01"
                    value={formData.MonthlyCharges}
                    onChange={handleChange}
                    className="w-full bg-[#222] border border-[#333] rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs uppercase text-gray-500 mb-1">Contract</label>
                  <select 
                    name="Contract" 
                    value={formData.Contract}
                    onChange={handleChange}
                    className="w-full bg-[#222] border border-[#333] rounded-lg p-3 text-sm focus:outline-none focus:border-blue-500"
                  >
                    <option value="Month-to-month">Month-to-month</option>
                    <option value="One year">One year</option>
                    <option value="Two year">Two year</option>
                  </select>
                </div>
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 transition-colors py-4 rounded-xl font-bold text-lg mt-6 shadow-lg shadow-blue-900/20 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Analyze Churn Risk"}
              </button>
            </form>
          </section>

          {/* Results Section */}
          <section>
            {!result && !error && (
              <div className="h-full flex flex-col items-center justify-center border-2 border-dashed border-[#262626] rounded-2xl p-12 text-center text-gray-500">
                <div className="w-16 h-16 bg-[#161616] rounded-full flex items-center justify-center mb-4">
                  🔍
                </div>
                <p>Run an analysis to see prediction results and AI risk factors here.</p>
              </div>
            )}

            {error && (
              <div className="bg-red-900/20 border border-red-900/50 rounded-2xl p-8 text-red-400">
                <h3 className="text-xl font-bold mb-2">Analysis Failed</h3>
                <p>{error}</p>
                <button onClick={reset} className="mt-4 text-sm underline">Try again</button>
              </div>
            )}

            {result && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                {/* Score Card */}
                <div className="bg-[#161616] border border-[#262626] rounded-2xl p-8 relative overflow-hidden">
                  <div className={`absolute top-0 right-0 w-32 h-32 blur-[80px] opacity-30 ${result.prediction_status === 'Churn' ? 'bg-red-500' : 'bg-green-500'}`}></div>
                  
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${result.prediction_status === 'Churn' ? 'bg-red-500/20 text-red-500' : 'bg-green-500/20 text-green-500'}`}>
                        {result.prediction_status}
                      </span>
                      <h3 className="text-3xl font-bold mt-2">{result.probability_percent}% <span className="text-lg font-normal text-gray-500">Probability</span></h3>
                    </div>
                  </div>
                  
                  <p className="text-gray-300 text-lg italic">&ldquo;{result.recommendation}&rdquo;</p>
                </div>

                {/* Risk Factors */}
                <div className="bg-[#161616] border border-[#262626] rounded-2xl p-8">
                  <h3 className="text-sm font-bold uppercase text-gray-500 tracking-widest mb-6">Key Risk Drivers (AI SHAP)</h3>
                  <div className="space-y-6">
                    {result.top_risk_factors.map((factor, index) => (
                      <div key={index}>
                        <div className="flex justify-between mb-2 text-sm">
                          <span className="text-gray-300">{factor.feature}</span>
                          <span className={`${factor.impact_score > 0 ? 'text-red-400' : 'text-green-400'}`}>
                            {factor.impact_score > 0 ? '↑ Risk' : '↓ Risk'}
                          </span>
                        </div>
                        <div className="h-2 w-full bg-[#262626] rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-1000 ${factor.impact_score > 0 ? 'bg-red-500' : 'bg-green-500'}`}
                            style={{ width: `${Math.min(100, Math.abs(factor.impact_score) * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
