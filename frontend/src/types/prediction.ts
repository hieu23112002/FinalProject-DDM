export interface CustomerData {
  gender: string;
  SeniorCitizen: number;
  Partner: string;
  Dependents: string;
  tenure: number;
  PhoneService: string;
  MultipleLines: string;
  InternetService: string;
  OnlineSecurity: string;
  OnlineBackup: string;
  DeviceProtection: string;
  TechSupport: string;
  StreamingTV: string;
  StreamingMovies: string;
  Contract: string;
  PaperlessBilling: string;
  PaymentMethod: string;
  MonthlyCharges: number;
  TotalCharges: string;
}

export interface RiskFactor {
  feature: string;
  impact_score: number;
}

export interface PredictionResult {
  prediction_status: string;
  probability_percent: number;
  top_risk_factors: RiskFactor[];
  recommendation: string;
}
