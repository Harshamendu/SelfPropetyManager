import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import {
  ManagedUser,
  UserCreate,
  UserPropertyAssignment,
  UserUpdate,
} from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class UserService {
  private api = inject(ApiService);

  list(): Observable<ManagedUser[]> {
    return this.api.get<ManagedUser[]>('/users');
  }

  get(id: string): Observable<ManagedUser> {
    return this.api.get<ManagedUser>(`/users/${id}`);
  }

  create(data: UserCreate): Observable<ManagedUser> {
    return this.api.post<ManagedUser>('/users', data);
  }

  update(id: string, data: UserUpdate): Observable<ManagedUser> {
    return this.api.put<ManagedUser>(`/users/${id}`, data);
  }

  deactivate(id: string): Observable<void> {
    return this.api.delete<void>(`/users/${id}`);
  }

  listAssignments(userId: string): Observable<UserPropertyAssignment[]> {
    return this.api.get<UserPropertyAssignment[]>(`/users/${userId}/properties`);
  }

  assignProperty(userId: string, propertyId: string): Observable<UserPropertyAssignment> {
    return this.api.post<UserPropertyAssignment>(`/users/${userId}/properties`, {
      property_id: propertyId,
    });
  }

  unassignProperty(userId: string, propertyId: string): Observable<void> {
    return this.api.delete<void>(`/users/${userId}/properties/${propertyId}`);
  }
}
