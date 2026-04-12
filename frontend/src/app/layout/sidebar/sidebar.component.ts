import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { PropertyService } from '../../features/properties/services/property.service';
import { Property } from '../../features/properties/models/property.model';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, MatListModule, MatIconModule, MatDividerModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent implements OnInit {
  private propertyService = inject(PropertyService);
  authService = inject(AuthService);
  properties: Property[] = [];

  get isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  get isTenant(): boolean {
    return this.authService.isTenant();
  }

  get isPropertyManager(): boolean {
    return this.authService.isPropertyManager();
  }

  get canManageProperties(): boolean {
    return this.isAdmin || this.isPropertyManager;
  }

  ngOnInit(): void {
    if (this.canManageProperties) {
      this.propertyService.getAll().subscribe({
        next: (props) => this.properties = props,
        error: () => this.properties = []
      });
    }
  }
}
