import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { AuthService } from '@core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatCardModule, MatFormFieldModule,
    MatInputModule, MatButtonModule, MatIconModule, MatTabsModule
  ],
  template: `
    <div class="login-container">
      <mat-card class="login-card">
        <div class="logo-section">
          <mat-icon class="logo-icon">apartment</mat-icon>
          <h1>Property Manager</h1>
        </div>

        <mat-tab-group>
          <mat-tab label="Login">
            <div class="form-content">
              <mat-form-field class="full-width">
                <mat-label>Email</mat-label>
                <input matInput [(ngModel)]="loginEmail" type="email" (keyup.enter)="login()">
              </mat-form-field>

              <mat-form-field class="full-width">
                <mat-label>Password</mat-label>
                <input matInput [(ngModel)]="loginPassword" [type]="hidePassword ? 'password' : 'text'" (keyup.enter)="login()">
                <button mat-icon-button matSuffix (click)="hidePassword = !hidePassword" type="button">
                  <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
                </button>
              </mat-form-field>

              @if (loginError) {
                <p class="error-text">{{ loginError }}</p>
              }

              <button mat-flat-button color="primary" class="full-width submit-btn" (click)="login()" [disabled]="loading">
                Login
              </button>
            </div>
          </mat-tab>

          <mat-tab label="Register">
            <div class="form-content">
              <mat-form-field class="full-width">
                <mat-label>Full Name</mat-label>
                <input matInput [(ngModel)]="registerName" (keyup.enter)="register()">
              </mat-form-field>

              <mat-form-field class="full-width">
                <mat-label>Email</mat-label>
                <input matInput [(ngModel)]="registerEmail" type="email" (keyup.enter)="register()">
              </mat-form-field>

              <mat-form-field class="full-width">
                <mat-label>Password</mat-label>
                <input matInput [(ngModel)]="registerPassword" [type]="hidePassword ? 'password' : 'text'" (keyup.enter)="register()">
                <button mat-icon-button matSuffix (click)="hidePassword = !hidePassword" type="button">
                  <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
                </button>
              </mat-form-field>

              @if (registerError) {
                <p class="error-text">{{ registerError }}</p>
              }

              <button mat-flat-button color="primary" class="full-width submit-btn" (click)="register()" [disabled]="loading">
                Create Account
              </button>
            </div>
          </mat-tab>
        </mat-tab-group>
      </mat-card>
    </div>
  `,
  styles: [`
    .login-container {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-primary);
    }

    .login-card {
      width: 420px;
      padding: 32px;
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
    }

    .logo-section {
      text-align: center;
      margin-bottom: 24px;

      .logo-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        color: var(--accent-primary);
      }

      h1 {
        font-size: 24px;
        font-weight: 400;
        margin-top: 8px;
        color: var(--text-primary);
      }
    }

    .form-content {
      padding: 24px 0 8px;
    }

    .full-width { width: 100%; }

    .submit-btn {
      height: 48px;
      font-size: 16px;
      margin-top: 8px;
    }

    .error-text {
      color: var(--accent-red);
      font-size: 13px;
      margin: -8px 0 12px;
    }
  `]
})
export class LoginComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  loginEmail = '';
  loginPassword = '';
  loginError = '';

  registerName = '';
  registerEmail = '';
  registerPassword = '';
  registerError = '';

  hidePassword = true;
  loading = false;

  login(): void {
    if (!this.loginEmail || !this.loginPassword) return;
    this.loading = true;
    this.loginError = '';
    this.authService.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate([this.landingRoute()]);
      },
      error: (err) => {
        this.loading = false;
        this.loginError = this.extractError(err, 'Login failed');
      }
    });
  }

  register(): void {
    if (!this.registerEmail || !this.registerPassword || !this.registerName) return;
    this.loading = true;
    this.registerError = '';
    this.authService.register(this.registerEmail, this.registerPassword, this.registerName).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate([this.landingRoute()]);
      },
      error: (err) => {
        this.loading = false;
        this.registerError = this.extractError(err, 'Registration failed');
      }
    });
  }

  private landingRoute(): string {
    return this.authService.isTenant() ? '/my-rental' : '/dashboard';
  }

  private extractError(err: any, fallback: string): string {
    const detail = err.error?.detail;
    if (!detail) return fallback;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join('; ');
    }
    return fallback;
  }
}
