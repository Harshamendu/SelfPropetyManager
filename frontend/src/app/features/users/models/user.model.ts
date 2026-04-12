import { UserRole } from '@core/services/auth.service';

export interface ManagedUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
  is_active?: boolean;
}

export interface UserUpdate {
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
  password?: string;
}

export interface UserPropertyAssignment {
  id: string;
  user_id: string;
  property_id: string;
  assigned_at: string;
}

export const USER_ROLES: { value: UserRole; label: string; description: string }[] = [
  { value: 'admin', label: 'Admin', description: 'Full access, manages users and all properties' },
  { value: 'property_manager', label: 'Property Manager', description: 'Full CRUD on assigned properties' },
  { value: 'tenant', label: 'Tenant', description: 'Sees only their own rental unit' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access on assigned properties' },
];
