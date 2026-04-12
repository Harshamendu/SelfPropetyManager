import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { BackupService, BackupInfo } from '../services/backup.service';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-backup-manager',
  standalone: true,
  imports: [
    CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatTableModule, MatProgressBarModule, MatSnackBarModule
  ],
  templateUrl: './backup-manager.component.html',
  styleUrl: './backup-manager.component.scss'
})
export class BackupManagerComponent implements OnInit {
  private backupService = inject(BackupService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  backups: BackupInfo[] = [];
  displayedColumns = ['filename', 'size', 'created_at', 'actions'];
  loading = true;
  creating = false;
  restoring = false;

  ngOnInit(): void {
    this.loadBackups();
  }

  loadBackups(): void {
    this.loading = true;
    this.backupService.list().subscribe({
      next: (backups) => {
        this.backups = backups;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  createBackup(): void {
    this.creating = true;
    this.backupService.create().subscribe({
      next: (backup) => {
        this.creating = false;
        this.snackBar.open(`Backup created: ${backup.filename}`, 'OK', { duration: 3000 });
        this.loadBackups();
      },
      error: () => {
        this.creating = false;
        this.snackBar.open('Backup failed!', 'OK', { duration: 3000 });
      }
    });
  }

  downloadBackup(backup: BackupInfo): void {
    this.backupService.download(backup.filename).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = backup.filename;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    });
  }

  restoreBackup(backup: BackupInfo): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Restore Database',
        message: `This will replace the current database with backup "${backup.filename}". All current data will be lost. Are you sure?`,
        confirmText: 'Restore'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.restoring = true;
        this.backupService.restore(backup.filename).subscribe({
          next: (res) => {
            this.restoring = false;
            this.snackBar.open(res.message, 'OK', { duration: 5000 });
          },
          error: () => {
            this.restoring = false;
            this.snackBar.open('Restore failed!', 'OK', { duration: 3000 });
          }
        });
      }
    });
  }

  deleteBackup(backup: BackupInfo): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Backup',
        message: `Delete backup "${backup.filename}"?`,
        confirmText: 'Delete'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.backupService.delete(backup.filename).subscribe({
          next: () => {
            this.snackBar.open('Backup deleted', 'OK', { duration: 2000 });
            this.loadBackups();
          }
        });
      }
    });
  }

  uploadBackup(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const file = input.files[0];
    if (!file.name.endsWith('.sql')) {
      this.snackBar.open('Only .sql backup files are accepted', 'OK', { duration: 3000 });
      return;
    }

    this.creating = true;
    this.backupService.upload(file).subscribe({
      next: (backup) => {
        this.creating = false;
        this.snackBar.open(`Uploaded: ${backup.filename}`, 'OK', { duration: 3000 });
        this.loadBackups();
        input.value = '';
      },
      error: () => {
        this.creating = false;
        this.snackBar.open('Upload failed!', 'OK', { duration: 3000 });
        input.value = '';
      }
    });
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }
}
