export type UserRole = 'customer' | 'farmer' | 'broker' | 'admin';

export interface Profile {
  id: string;
  full_name: string;
  phone_number: string;
  national_id: string;
  role: UserRole;
  preferred_language: string;
  is_phone_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile: Profile;
}

export interface AuthResponse {
  token?: string;
  access?: string;
  access_token?: string;
  refresh?: string;
  user?: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  phone_number?: string;
  national_id?: string;
  role?: UserRole;
  preferred_language?: 'en' | 'sw';
}

export interface LandParcel {
  id: string;
  name: string;
  ward_code: string;
  h3_index: string;
  acreage: string;
  is_primary: boolean;
  verified: boolean;
}

export interface FarmerOnboarding {
  id: string;
  profile: string;
  ward_code: string;
  crop: string;
  acreage: string;
  mpesa_number: string;
  verification_level: number;
  stage_label: string;
  status: string;
  notes: string;
  submitted_at: string | null;
  approved_at: string | null;
  rejection_reason: string;
  land_parcels: LandParcel[];
  created_at: string;
  updated_at: string;
}

export interface PolicyEvent {
  id: string;
  event_type: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface Policy {
  id: string;
  onboarding: string;
  policy_number: string;
  crop: string;
  insured_acreage: string;
  coverage_h3: string;
  premium_amount: string;
  coverage_start: string;
  coverage_end: string;
  mitigation_discount_percent: string;
  status: string;
  metadata: Record<string, unknown>;
  events?: PolicyEvent[];
  farmer_name?: string;
  farmer_phone?: string;
  ward_name?: string;
  constituency_name?: string;
  subcounty_name?: string;
  county_name?: string;
  created_at: string;
  updated_at: string;
}

export interface ClaimReview {
  id: string;
  reviewed_by: number | null;
  decision: string;
  notes: string;
  created_at: string;
}

export interface Claim {
  id: string;
  policy: string;
  claim_number: string;
  loss_type: string;
  description: string;
  claimed_amount: string;
  trigger_value: string;
  threshold_value: string;
  evidence: Record<string, unknown>;
  status: string;
  reviews?: ClaimReview[];
  created_at: string;
  updated_at: string;
}

export interface Payout {
  id: string;
  policy: string;
  amount: string;
  phone_number: string;
  reference: string;
  status: string;
  tx_hash: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  error?: string;
  [key: string]: unknown;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface SimulateDroughtPayload {
  h3_index: string;
  rainfall_mm?: number;
  ndvi?: number;
}

export interface TriggerEvaluationPayload {
  h3_index: string;
  simulate_drought?: boolean;
}

export interface RegisterFarmerPayload {
  username: string;
  email: string;
  password: string;
  full_name: string;
  phone_number: string;
  ward_code: string;
  crop: string;
  acreage: string;
  mpesa_number: string;
  h3_index: string;
}
