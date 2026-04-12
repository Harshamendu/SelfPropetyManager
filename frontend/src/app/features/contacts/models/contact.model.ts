export interface Contact {
  id: string;
  property_id?: string;
  user_id?: string;
  contact_type: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  company?: string;
  address?: string;
  notes?: string;
  lease_start?: string;
  lease_end?: string;
  monthly_rent?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ContactCreate {
  property_id?: string;
  user_id?: string;
  contact_type: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  company?: string;
  address?: string;
  notes?: string;
  lease_start?: string;
  lease_end?: string;
  monthly_rent?: number;
}

export const CONTACT_TYPES = [
  'tenant',
  'contractor',
  'agent',
  'hoa',
  'insurance',
  'other'
];
