export interface RentalPayment {
  id: string;
  property_id?: string;
  tenant_contact_id?: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  period_start: string;
  period_end: string;
  category?: string;
  is_recurring: boolean;
  recurrence_rule?: string;
  recurring_day?: number;
  is_marked_done: boolean;
  notes?: string;
  created_at: string;
}

export interface RentalPaymentCreate {
  tenant_contact_id?: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  period_start: string;
  period_end: string;
  category?: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
  recurring_day?: number;
  is_marked_done?: boolean;
  notes?: string;
}

export const PAYMENT_METHODS = [
  'check',
  'bank_transfer',
  'cash',
  'zelle',
  'venmo',
  'other'
];
