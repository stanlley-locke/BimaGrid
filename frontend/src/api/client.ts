import type {
  ApiError,
  AuthResponse,
  Claim,
  FarmerOnboarding,
  HealthResponse,
  LoginCredentials,
  PaginatedResponse,
  Payout,
  Policy,
  RegisterFarmerPayload,
  RegisterPayload,
  SimulateDroughtPayload,
  TriggerEvaluationPayload,
  User,
} from '../types';

const TOKEN_KEY = 'bimagrid_auth_token';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '/api';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function extractToken(data: AuthResponse): string | null {
  return data.token || data.access || data.access_token || null;
}

function extractErrorMessage(data: ApiError, fallback: string): string {
  if (typeof data.detail === 'string') return data.detail;
  if (typeof data.message === 'string') return data.message;
  if (typeof data.error === 'string') return data.error;

  const firstFieldError = Object.values(data).find(
    (value) => Array.isArray(value) && typeof value[0] === 'string',
  ) as string[] | undefined;

  if (firstFieldError?.[0]) return firstFieldError[0];
  return fallback;
}

export class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) return {} as T;
  return JSON.parse(text) as T;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  if (authenticated) {
    const token = getStoredToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await parseJson<ApiError>(response);
    throw new ApiClientError(
      extractErrorMessage(errorData, `Request failed (${response.status})`),
      response.status,
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return parseJson<T>(response);
}

function normalizeList<T>(data: T[] | PaginatedResponse<T>): T[] {
  if (Array.isArray(data)) return data;
  return data.results ?? [];
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<{ token: string; user?: User }> {
    const endpoints = ['/accounts/login/', '/auth/token/', '/accounts/token/'];

    let lastError: ApiClientError | null = null;

    for (const endpoint of endpoints) {
      try {
        const data = await apiRequest<AuthResponse>(
          endpoint,
          {
            method: 'POST',
            body: JSON.stringify(credentials),
          },
          false,
        );

        const token = extractToken(data);
        if (!token) {
          throw new ApiClientError('Authentication response did not include a token.', 500);
        }

        setStoredToken(token);
        return { token, user: data.user };
      } catch (error) {
        if (error instanceof ApiClientError && error.status === 404) {
          lastError = error;
          continue;
        }
        throw error;
      }
    }

    throw lastError ?? new ApiClientError('Login endpoint not available.', 404);
  },

  async register(payload: RegisterPayload): Promise<User> {
    return apiRequest<User>(
      '/accounts/register/',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      false,
    );
  },

  async me(): Promise<User> {
    return apiRequest<User>('/accounts/me/');
  },

  logout(): void {
    clearStoredToken();
  },
};

export const dashboardApi = {
  async getPolicies(): Promise<Policy[]> {
    const data = await apiRequest<Policy[] | PaginatedResponse<Policy>>('/policies/');
    return normalizeList(data);
  },

  async getClaims(): Promise<Claim[]> {
    const data = await apiRequest<Claim[] | PaginatedResponse<Claim>>('/claims/');
    return normalizeList(data);
  },

  async getPayouts(): Promise<Payout[]> {
    const data = await apiRequest<Payout[] | PaginatedResponse<Payout>>('/payments/payouts/');
    return normalizeList(data);
  },

  async getOnboarding(): Promise<FarmerOnboarding> {
    return apiRequest<FarmerOnboarding>('/onboarding/');
  },

  async updateOnboarding(payload: Partial<FarmerOnboarding>): Promise<FarmerOnboarding> {
    return apiRequest<FarmerOnboarding>('/onboarding/', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  async submitOnboarding(payload: Partial<FarmerOnboarding>): Promise<FarmerOnboarding> {
    return apiRequest<FarmerOnboarding>('/onboarding/submit/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async registerFarmer(payload: RegisterFarmerPayload): Promise<User> {
    return apiRequest<User>(
      '/accounts/register/',
      {
        method: 'POST',
        body: JSON.stringify({
          ...payload,
          role: 'farmer',
        }),
      },
      true,
    );
  },

  async getCounties(): Promise<{ id: string; external_id: number; name: string }[]> {
    const data = await apiRequest<{ id: string; external_id: number; name: string }[] | PaginatedResponse<{ id: string; external_id: number; name: string }>>('/geography/counties/');
    return normalizeList(data);
  },

  async getSubcounties(countyId: string): Promise<{ id: string; external_id: number; name: string }[]> {
    const data = await apiRequest<{ id: string; external_id: number; name: string }[] | PaginatedResponse<{ id: string; external_id: number; name: string }>>(`/geography/counties/${countyId}/subcounties/`);
    return normalizeList(data);
  },

  async getConstituencies(subcountyId: string): Promise<{ id: string; external_id: number; name: string }[]> {
    const data = await apiRequest<{ id: string; external_id: number; name: string }[] | PaginatedResponse<{ id: string; external_id: number; name: string }>>(`/geography/subcounties/${subcountyId}/constituencies/`);
    return normalizeList(data);
  },

  async getWards(constituencyId: string): Promise<{ id: string; external_id: number; ward_code: string; name: string }[]> {
    const data = await apiRequest<{ id: string; external_id: number; ward_code: string; name: string }[] | PaginatedResponse<{ id: string; external_id: number; ward_code: string; name: string }>>(`/geography/wards/?constituency_id=${constituencyId}`);
    return normalizeList(data);
  },

  async getRainfall(h3Index: string): Promise<{ h3_index: string; metric: string; value: number }> {
    return apiRequest<{ h3_index: string; metric: string; value: number }>(`/satellite/rainfall/?h3_index=${h3Index}`);
  },

  async getNdvi(h3Index: string): Promise<{ h3_index: string; metric: string; value: number }> {
    return apiRequest<{ h3_index: string; metric: string; value: number }>(`/satellite/ndvi/?h3_index=${h3Index}`);
  },

  async simulateDrought(payload: SimulateDroughtPayload): Promise<Record<string, unknown>> {
    return apiRequest<Record<string, unknown>>('/admin/simulate-drought/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async triggerEvaluation(payload: TriggerEvaluationPayload): Promise<Record<string, unknown>> {
    return apiRequest<Record<string, unknown>>('/admin/trigger-evaluation/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async health(): Promise<HealthResponse> {
    const base = API_BASE_URL.replace(/\/api$/, '');
    const response = await fetch(`${base}/health/`);
    if (!response.ok) {
      throw new ApiClientError('Backend health check failed.', response.status);
    }
    return response.json() as Promise<HealthResponse>;
  },
};
