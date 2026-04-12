import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';

export interface BackupInfo {
  filename: string;
  size_bytes: number;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class BackupService {
  private api = inject(ApiService);

  list(): Observable<BackupInfo[]> {
    return this.api.get<BackupInfo[]>('/backups');
  }

  create(): Observable<BackupInfo> {
    return this.api.post<BackupInfo>('/backups');
  }

  download(filename: string): Observable<Blob> {
    return this.api.downloadBlob(`/backups/${filename}/download`);
  }

  restore(filename: string): Observable<{ message: string }> {
    return this.api.post<{ message: string }>(`/backups/restore/${filename}`);
  }

  delete(filename: string): Observable<void> {
    return this.api.delete<void>(`/backups/${filename}`);
  }

  upload(file: File): Observable<BackupInfo> {
    const formData = new FormData();
    formData.append('file', file);
    return this.api.upload<BackupInfo>('/backups/upload', formData);
  }
}
