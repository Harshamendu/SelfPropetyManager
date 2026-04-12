export interface Category {
  id: string;
  property_id?: string;
  name: string;
  category_type: 'expense' | 'payment';
  is_recurring: boolean;
  requires_marking: boolean;
  default_recurrence_rule?: string;
  created_at: string;
}

export interface CategoryCreate {
  property_id?: string;
  name: string;
  category_type: 'expense' | 'payment';
  is_recurring: boolean;
  requires_marking: boolean;
  default_recurrence_rule?: string;
}
