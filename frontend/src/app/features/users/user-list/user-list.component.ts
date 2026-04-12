import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { UserService } from '../services/user.service';
import { ManagedUser, USER_ROLES } from '../models/user.model';
import { UserRole, AuthService } from '@core/services/auth.service';
import { UserFormComponent } from '../user-form/user-form.component';
import { UserPropertiesDialogComponent } from '../user-properties-dialog/user-properties-dialog.component';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatChipsModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTooltipModule,
  ],
  templateUrl: './user-list.component.html',
  styleUrl: './user-list.component.scss',
})
export class UserListComponent implements OnInit {
  private userService = inject(UserService);
  private authService = inject(AuthService);
  private dialog = inject(MatDialog);
  private snack = inject(MatSnackBar);

  users: ManagedUser[] = [];
  loading = true;
  displayedColumns = ['full_name', 'email', 'role', 'is_active', 'actions'];

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.userService.list().subscribe({
      next: (users) => {
        this.users = users;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  roleLabel(role: UserRole): string {
    return USER_ROLES.find((r) => r.value === role)?.label ?? role;
  }

  openCreate(): void {
    const ref = this.dialog.open(UserFormComponent, {
      width: '520px',
      data: { user: null },
    });
    ref.afterClosed().subscribe((created) => {
      if (created) {
        this.load();
        if (created.role === 'property_manager' || created.role === 'viewer') {
          this.snack.open('User created. Assign properties next.', 'Assign', {
            duration: 6000,
          }).onAction().subscribe(() => this.openAssignments(created));
        } else {
          this.snack.open('User created', 'Dismiss', { duration: 4000 });
        }
      }
    });
  }

  openEdit(user: ManagedUser): void {
    const ref = this.dialog.open(UserFormComponent, {
      width: '520px',
      data: { user },
    });
    ref.afterClosed().subscribe((updated) => {
      if (updated) this.load();
    });
  }

  openAssignments(user: ManagedUser): void {
    this.dialog.open(UserPropertiesDialogComponent, {
      width: '560px',
      data: { user },
    });
  }

  deactivate(user: ManagedUser): void {
    if (user.id === this.authService.currentUser?.id) {
      this.snack.open('You cannot deactivate your own account', 'Dismiss', { duration: 4000 });
      return;
    }
    const ref = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Deactivate user',
        message: `Deactivate "${user.full_name}"? They will no longer be able to log in.`,
        confirmText: 'Deactivate',
      },
    });
    ref.afterClosed().subscribe((confirmed) => {
      if (confirmed) {
        this.userService.deactivate(user.id).subscribe({
          next: () => {
            this.snack.open('User deactivated', 'Dismiss', { duration: 3000 });
            this.load();
          },
        });
      }
    });
  }

  reactivate(user: ManagedUser): void {
    this.userService.update(user.id, { is_active: true }).subscribe({
      next: () => {
        this.snack.open('User reactivated', 'Dismiss', { duration: 3000 });
        this.load();
      },
    });
  }
}
