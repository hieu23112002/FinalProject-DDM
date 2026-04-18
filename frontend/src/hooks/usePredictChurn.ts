import { useState } from "react";
import { CustomerData, PredictionResult } from "@/types/prediction";
import { predictChurn } from "@/lib/api";

export function usePredictChurn() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);

  const predict = async (data: CustomerData) => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictChurn(data);
      setResult(res);
      return res;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Something went wrong";
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return { predict, loading, error, result, reset };
}
