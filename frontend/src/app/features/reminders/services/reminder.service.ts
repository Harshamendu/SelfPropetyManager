import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { Reminder, ReminderCreate } from '../models/reminder.model';

@Injectable({ providedIn: 'root' })
export class ReminderService {
  private api = inject(ApiService);

  getByProperty(propertyId: string): Observable<Reminder[]> {
    return this.api.get<Reminder[]>(`/reminders?property_id=${propertyId}`);
  }

  create(data: ReminderCreate): Observable<Reminder> {
    return this.api.post<Reminder>('/reminders', data);
  }

  update(id: string, data: Partial<ReminderCreate>): Observable<Reminder> {
    return this.api.put<Reminder>(`/reminders/${id}`, data);
  }

  complete(id: string): Observable<Reminder> {
    return this.api.patch<Reminder>(`/reminders/${id}/complete`);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/reminders/${id}`);
  }
}
