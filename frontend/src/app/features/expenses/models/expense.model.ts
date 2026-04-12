export interface Expense {
  id: string;
  property_id?: string;
  category: string;
  description: string;
  amount: number;
  date: string;
  is_recurring: boolean;
  recurrence_rule?: string;
  recurring_day?: number;
  is_marked_done: boolean;
  vendor?: string;
  receipt_document_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface ExpenseCreate {
  category: string;
  description: string;
  amount: number;
  date: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
  recurring_day?: number;
  is_marked_done?: boolean;
  vendor?: string;
}
