import { Component, Input, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { ReminderService } from '../services/reminder.service';
import { Reminder } from '../models/reminder.model';
import { ReminderFormComponent } from '../reminder-form/reminder-form.component';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-reminder-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatIconModule, MatChipsModule],
  templateUrl: './reminder-list.component.html',
  styleUrl: './reminder-list.component.scss'
})
export class ReminderListComponent implements OnInit {
  @Input({ required: true }) propertyId!: string;

  private reminderService = inject(ReminderService);
  private dialog = inject(MatDialog);

  reminders: Reminder[] = [];
  displayedColumns = ['title', 'due_date', 'reminder_type', 'status', 'is_recurring', 'actions'];
  loading = true;

  ngOnInit(): void {
    this.loadReminders();
  }

  loadReminders(): void {
    this.loading = true;
    this.reminderService.getByProperty(this.propertyId).subscribe({
      next: (reminders) => {
        this.reminders = reminders;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  addReminder(): void {
    const dialogRef = this.dialog.open(ReminderFormComponent, {
      width: '500px',
      data: { propertyId: this.propertyId }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) this.loadReminders();
    });
  }

  editReminder(reminder: Reminder): void {
    const dialogRef = this.dialog.open(ReminderFormComponent, {
      width: '500px',
      data: { propertyId: this.propertyId, reminder }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) this.loadReminders();
    });
  }

  completeReminder(reminder: Reminder): void {
    this.reminderService.complete(reminder.id).subscribe({
      next: () => this.loadReminders()
    });
  }

  deleteReminder(reminder: Reminder): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Reminder',
        message: `Delete reminder "${reminder.title}"?`,
        confirmText: 'Delete'
      }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.reminderService.delete(reminder.id).subscribe({
          next: () => this.loadReminders()
        });
      }
    });
  }

  isOverdue(reminder: Reminder): boolean {
    return new Date(reminder.due_date) < new Date() && !reminder.is_completed;
  }

  getStatus(reminder: Reminder): string {
    if (reminder.is_completed) return 'Completed';
    if (this.isOverdue(reminder)) return 'Overdue';
    return 'Pending';
  }
}
