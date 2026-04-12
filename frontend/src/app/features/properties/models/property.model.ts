export interface Property {
  id: string;
  name: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: string;
  purchase_date?: string;
  purchase_price?: number;
  notes?: string;
  landlord_name?: string;
  landlord_phone?: string;
  landlord_email?: string;
  landlord_address?: string;
  created_at: string;
  updated_at: string;
}

export interface PropertyCreate {
  name: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: string;
  purchase_date?: string;
  purchase_price?: number;
  notes?: string;
  landlord_name?: string;
  landlord_phone?: string;
  landlord_email?: string;
  landlord_address?: string;
}

export interface PropertyUpdate extends Partial<PropertyCreate> {}

export interface LeaseSummary {
  tenant_name: string;
  lease_start?: string;
  lease_end?: string;
  monthly_rent?: number;
}

export interface PropertySummary {
  id: string;
  name: string;
  address_line1: string;
  city: string;
  state: string;
  is_leased: boolean;
  lease?: LeaseSummary;
  rent_collected_ytd: number;
  expenses_ytd: number;
  upcoming_reminders: number;
}
