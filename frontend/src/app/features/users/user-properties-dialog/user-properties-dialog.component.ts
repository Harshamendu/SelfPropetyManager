import { Component, Inject, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { forkJoin } from 'rxjs';
import { UserService } from '../services/user.service';
import { ManagedUser, UserPropertyAssignment } from '../models/user.model';
import { PropertyService } from '@features/properties/services/property.service';
import { Property } from '@features/properties/models/property.model';

interface AssignmentRow {
  assignment: UserPropertyAssignment;
  property?: Property;
}

@Component({
  selector: 'app-user-properties-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
  ],
  templateUrl: './user-properties-dialog.component.html',
  styleUrl: './user-properties-dialog.component.scss',
})
export class UserPropertiesDialogComponent implements OnInit {
  private userService = inject(UserService);
  private propertyService = inject(PropertyService);
  private dialogRef = inject(MatDialogRef<UserPropertiesDialogComponent>);

  user: ManagedUser;
  allProperties: Property[] = [];
  rows: AssignmentRow[] = [];
  selectedPropertyId = '';
  loading = true;

  constructor(@Inject(MAT_DIALOG_DATA) public data: { user: ManagedUser }) {
    this.user = data.user;
  }

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    forkJoin({
      properties: this.propertyService.getAll(),
      assignments: this.userService.listAssignments(this.user.id),
    }).subscribe({
      next: ({ properties, assignments }) => {
        this.allProperties = properties;
        this.rows = assignments.map((a) => ({
          assignment: a,
          property: properties.find((p) => p.id === a.property_id),
        }));
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  get availableProperties(): Property[] {
    const assigned = new Set(this.rows.map((r) => r.assignment.property_id));
    return this.allProperties.filter((p) => !assigned.has(p.id));
  }

  assign(): void {
    if (!this.selectedPropertyId) return;
    this.userService.assignProperty(this.user.id, this.selectedPropertyId).subscribe({
      next: () => {
        this.selectedPropertyId = '';
        this.load();
      },
    });
  }

  unassign(propertyId: string): void {
    this.userService.unassignProperty(this.user.id, propertyId).subscribe({
      next: () => this.load(),
    });
  }

  close(): void {
    this.dialogRef.close();
  }
}
