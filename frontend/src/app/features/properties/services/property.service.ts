import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { Property, PropertyCreate, PropertyUpdate, PropertySummary } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class PropertyService {
  private api = inject(ApiService);

  getAll(): Observable<Property[]> {
    return this.api.get<Property[]>('/properties');
  }

  getById(id: string): Observable<Property> {
    return this.api.get<Property>(`/properties/${id}`);
  }

  create(data: PropertyCreate): Observable<Property> {
    return this.api.post<Property>('/properties', data);
  }

  update(id: string, data: PropertyUpdate): Observable<Property> {
    return this.api.put<Property>(`/properties/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/properties/${id}`);
  }

  getSummary(id: string, year: number): Observable<PropertySummary> {
    return this.api.get<PropertySummary>(`/properties/${id}/summary`, { year });
  }
}
