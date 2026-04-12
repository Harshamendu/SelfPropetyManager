import { Component, Inject, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import {
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { UserService } from '../services/user.service';
import { ManagedUser, USER_ROLES } from '../models/user.model';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatCheckboxModule,
    MatIconModule,
  ],
  templateUrl: './user-form.component.html',
  styleUrl: './user-form.component.scss',
})
export class UserFormComponent {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  private dialogRef = inject(MatDialogRef<UserFormComponent>);

  roles = USER_ROLES;
  loading = false;
  error = '';
  isEdit = false;

  form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    full_name: ['', Validators.required],
    role: ['property_manager' as const, Validators.required],
    password: [''],
    is_active: [true],
  });

  constructor(@Inject(MAT_DIALOG_DATA) public data: { user: ManagedUser | null }) {
    if (data.user) {
      this.isEdit = true;
      this.form.patchValue({
        email: data.user.email,
        full_name: data.user.full_name,
        role: data.user.role as any,
        is_active: data.user.is_active,
      });
      this.form.get('email')?.disable();
      this.form.get('password')?.clearValidators();
    } else {
      this.form.get('password')?.setValidators([Validators.required, Validators.minLength(8)]);
    }
    this.form.get('password')?.updateValueAndValidity();
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    const raw = this.form.getRawValue();

    if (this.isEdit && this.data.user) {
      const update: any = {
        full_name: raw.full_name,
        role: raw.role,
        is_active: raw.is_active,
      };
      if (raw.password) update.password = raw.password;
      this.userService.update(this.data.user.id, update).subscribe({
        next: (u) => this.dialogRef.close(u),
        error: (err) => {
          this.error = this.extractError(err);
          this.loading = false;
        },
      });
    } else {
      this.userService
        .create({
          email: raw.email!,
          full_name: raw.full_name!,
          role: raw.role!,
          password: raw.password!,
          is_active: raw.is_active ?? true,
        })
        .subscribe({
          next: (u) => this.dialogRef.close(u),
          error: (err) => {
            this.error = this.extractError(err);
            this.loading = false;
          },
        });
    }
  }

  private extractError(err: any): string {
    const d = err?.error?.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return d.map((e: any) => e.msg).join(', ');
    return 'Failed to save user';
  }

  cancel(): void {
    this.dialogRef.close(null);
  }
}
