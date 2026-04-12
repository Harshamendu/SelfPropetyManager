import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { Contact, ContactCreate } from '../models/contact.model';

@Injectable({ providedIn: 'root' })
export class ContactService {
  private api = inject(ApiService);

  getByProperty(propertyId: string): Observable<Contact[]> {
    return this.api.get<Contact[]>(`/properties/${propertyId}/contacts`);
  }

  create(data: ContactCreate): Observable<Contact> {
    return this.api.post<Contact>('/contacts', data);
  }

  update(id: string, data: Partial<ContactCreate>): Observable<Contact> {
    return this.api.put<Contact>(`/contacts/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/contacts/${id}`);
  }
}
