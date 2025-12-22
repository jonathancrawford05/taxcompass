/**
 * API Client
 * Handles all backend API communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UserProfile {
  citizenship: string[];
  current_country: string;
  destination_country: string;
  departure_date: string;
  marital_status: 'single' | 'married' | 'common_law';
  has_spouse: boolean;
  spouse_location?: string;
  has_dependents: boolean;
  dependents_location?: string;
  owns_home_origin: boolean;
  home_disposition?: 'sell' | 'rent' | 'keep_vacant';
  owns_home_destination: boolean;
  employment_type: 'employee' | 'self_employed' | 'business_owner';
  employer_country: string;
  annual_income: string;
  has_rental_property?: boolean;
  investment_accounts_balance?: string;
  rrsp_balance?: string;
  tfsa_balance?: string;
  unrealized_capital_gains?: string;
}

export interface AnalysisRequest {
  title?: string;
  origin_country: string;
  destination_country: string;
  departure_date: string;
  user_profile: UserProfile;
}

export interface Analysis {
  id: string;
  user_id: string;
  title: string;
  origin_country: string;
  destination_country: string;
  departure_date: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  origin_residency_status?: string;
  destination_residency_status?: string;
  confidence_score?: number;
  key_factors?: string[];
  recommendations?: string[];
  red_flags?: string[];
  reasoning?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async quickAnalysis(request: AnalysisRequest): Promise<Analysis> {
    const response = await fetch(`${this.baseUrl}/api/v1/analysis/quick-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Analysis failed: ${error}`);
    }

    return response.json();
  }

  async getAnalysis(id: string): Promise<Analysis> {
    const response = await fetch(`${this.baseUrl}/api/v1/analysis/${id}`);

    if (!response.ok) {
      throw new Error('Failed to fetch analysis');
    }

    return response.json();
  }

  async listAnalyses(): Promise<Analysis[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/analysis`);

    if (!response.ok) {
      throw new Error('Failed to fetch analyses');
    }

    return response.json();
  }

  async getDiagnostics(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/diagnostics`);

    if (!response.ok) {
      throw new Error('Failed to fetch diagnostics');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
