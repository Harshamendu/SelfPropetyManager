import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { DocumentTemplate, TemplateCreate } from '../models/template.model';

@Injectable({ providedIn: 'root' })
export class DocumentGenService {
  private api = inject(ApiService);

  getAll(state?: string): Observable<DocumentTemplate[]> {
    const params = state ? `?state=${state}` : '';
    return this.api.get<DocumentTemplate[]>(`/document-templates${params}`);
  }

  getById(id: string): Observable<DocumentTemplate> {
    return this.api.get<DocumentTemplate>(`/document-templates/${id}`);
  }

  create(data: TemplateCreate): Observable<DocumentTemplate> {
    return this.api.post<DocumentTemplate>('/document-templates', data);
  }

  update(id: string, data: Partial<TemplateCreate>): Observable<DocumentTemplate> {
    return this.api.put<DocumentTemplate>(`/document-templates/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/document-templates/${id}`);
  }

  seedTemplates(state: string): Observable<DocumentTemplate[]> {
    return this.api.post<DocumentTemplate[]>(`/document-templates/seed/${state}`, {});
  }

  getContext(propertyId: string): Observable<Record<string, string>> {
    return this.api.get<Record<string, string>>(`/document-templates/context/${propertyId}`);
  }

  generate(templateId: string, variables: Record<string, string>): Observable<Blob> {
    return this.api.postBlob(`/document-templates/${templateId}/generate`, { variables });
  }

  preview(templateId: string, variables: Record<string, string>): Observable<{ rendered: string }> {
    return this.api.post<{ rendered: string }>(`/document-templates/${templateId}/preview`, { variables });
  }
}
