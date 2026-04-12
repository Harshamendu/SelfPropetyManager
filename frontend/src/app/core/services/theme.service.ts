import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type ThemeMode = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private themeSubject = new BehaviorSubject<ThemeMode>(this.getStoredTheme());
  theme$ = this.themeSubject.asObservable();

  get currentTheme(): ThemeMode {
    return this.themeSubject.value;
  }

  get isDark(): boolean {
    return this.currentTheme === 'dark';
  }

  constructor() {
    this.applyTheme(this.currentTheme);
  }

  toggle(): void {
    const next = this.isDark ? 'light' : 'dark';
    this.setTheme(next);
  }

  setTheme(mode: ThemeMode): void {
    localStorage.setItem('theme', mode);
    this.themeSubject.next(mode);
    this.applyTheme(mode);
  }

  private getStoredTheme(): ThemeMode {
    return (localStorage.getItem('theme') as ThemeMode) || 'light';
  }

  private applyTheme(mode: ThemeMode): void {
    document.body.classList.remove('light-theme', 'dark-theme');
    document.body.classList.add(`${mode}-theme`);
  }
}
