import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { ContactService } from '../services/contact.service';
import { Contact, CONTACT_TYPES } from '../models/contact.model';
import { AuthService } from '@core/services/auth.service';
import { UserService } from '@features/users/services/user.service';
import { ManagedUser } from '@features/users/models/user.model';

@Component({
  selector: 'app-contact-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatDialogModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatButtonModule, MatDatepickerModule, MatNativeDateModule
  ],
  templateUrl: './contact-form.component.html'
})
export class ContactFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ContactFormComponent>);
  private data: { propertyId: string; contact?: Contact } = inject(MAT_DIALOG_DATA);
  private contactService = inject(ContactService);
  private authService = inject(AuthService);
  private userService = inject(UserService);

  form!: FormGroup;
  contactTypes = CONTACT_TYPES;
  isEditMode = false;
  saving = false;
  isAdmin = false;
  tenantUsers: ManagedUser[] = [];

  ngOnInit(): void {
    this.isEditMode = !!this.data.contact;
    this.isAdmin = this.authService.isAdmin();
    const c = this.data.contact;

    this.form = this.fb.group({
      contact_type: [c?.contact_type || '', Validators.required],
      first_name: [c?.first_name || '', Validators.required],
      last_name: [c?.last_name || '', Validators.required],
      email: [c?.email || '', Validators.email],
      phone: [c?.phone || ''],
      company: [c?.company || ''],
      address: [c?.address || ''],
      notes: [c?.notes || ''],
      lease_start: [c?.lease_start ? new Date(c.lease_start) : null],
      lease_end: [c?.lease_end ? new Date(c.lease_end) : null],
      monthly_rent: [c?.monthly_rent || null],
      user_id: [c?.user_id || null]
    });

    if (this.isAdmin) {
      this.userService.list().subscribe({
        next: (users) => {
          this.tenantUsers = users.filter(
            (u) => u.role === 'tenant' && u.is_active,
          );
        },
        error: () => (this.tenantUsers = []),
      });
    }
  }

  save(): void {
    if (this.form.invalid) return;

    this.saving = true;
    const formValue = { ...this.form.value, property_id: this.data.propertyId };

    ['lease_start', 'lease_end'].forEach(field => {
      if (formValue[field]) {
        const d = new Date(formValue[field]);
        formValue[field] = d.toISOString().split('T')[0];
      }
    });

    const request$ = this.isEditMode
      ? this.contactService.update(this.data.contact!.id, formValue)
      : this.contactService.create(formValue);

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
