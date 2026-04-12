import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { ReminderService } from '../services/reminder.service';
import { Reminder, REMINDER_TYPES, RECURRENCE_RULES } from '../models/reminder.model';

@Component({
  selector: 'app-reminder-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatDialogModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatDatepickerModule, MatNativeDateModule,
    MatButtonModule, MatCheckboxModule
  ],
  templateUrl: './reminder-form.component.html'
})
export class ReminderFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ReminderFormComponent>);
  private data: { propertyId: string; reminder?: Reminder } = inject(MAT_DIALOG_DATA);
  private reminderService = inject(ReminderService);

  form!: FormGroup;
  reminderTypes = REMINDER_TYPES;
  recurrenceRules = RECURRENCE_RULES;
  isEditMode = false;
  saving = false;

  ngOnInit(): void {
    this.isEditMode = !!this.data.reminder;
    const r = this.data.reminder;

    this.form = this.fb.group({
      title: [r?.title || '', Validators.required],
      description: [r?.description || ''],
      due_date: [r?.due_date ? new Date(r.due_date) : new Date(), Validators.required],
      reminder_type: [r?.reminder_type || '', Validators.required],
      is_recurring: [r?.is_recurring || false],
      recurrence_rule: [r?.recurrence_rule || ''],
      notify_email: [r?.notify_email || false],
      notify_in_app: [r?.notify_in_app ?? true]
    });
  }

  save(): void {
    if (this.form.invalid) return;

    this.saving = true;
    const formValue = { ...this.form.value, property_id: this.data.propertyId };
    if (formValue.due_date) {
      formValue.due_date = new Date(formValue.due_date).toISOString();
    }

    const request$ = this.isEditMode
      ? this.reminderService.update(this.data.reminder!.id, formValue)
      : this.reminderService.create(formValue);

    request$.subscribe({
      next: () => {
        this.saving = false;
        this.dialogRef.close(true);
      },
      error: () => this.saving = false
    });
  }

  cancel(): void {
    this.dialogRef.close(false);
  }
}
