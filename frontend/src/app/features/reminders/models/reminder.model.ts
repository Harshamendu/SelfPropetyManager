export interface Reminder {
  id: string;
  property_id?: string;
  title: string;
  description?: string;
  due_date: string;
  reminder_type: string;
  is_recurring: boolean;
  recurrence_rule?: string;
  notify_email: boolean;
  notify_in_app: boolean;
  is_completed: boolean;
  completed_at?: string;
  email_sent: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ReminderCreate {
  property_id?: string;
  title: string;
  description?: string;
  due_date: string;
  reminder_type: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
  notify_email?: boolean;
  notify_in_app?: boolean;
}

export const REMINDER_TYPES = [
  'lease_renewal',
  'tenant_call',
  'maintenance',
  'payment',
  'inspection',
  'other'
];

export const RECURRENCE_RULES = [
  'monthly',
  'quarterly',
  'annually'
];
