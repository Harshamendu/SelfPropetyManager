import { Injectable, inject, OnDestroy } from '@angular/core';
import { BehaviorSubject, interval, Subscription, switchMap } from 'rxjs';
import { ApiService } from './api.service';

interface UnreadCountResponse {
  unread_count: number;
}

@Injectable({ providedIn: 'root' })
export class NotificationService implements OnDestroy {
  private api = inject(ApiService);
  private pollSubscription: Subscription | null = null;

  unreadCount$ = new BehaviorSubject<number>(0);

  constructor() {
    this.loadUnreadCount();
    this.pollSubscription = interval(60000)
      .pipe(switchMap(() => this.api.get<UnreadCountResponse>('/notifications/unread-count')))
      .subscribe({
        next: (res) => this.unreadCount$.next(res.unread_count),
        error: () => {}
      });
  }

  loadUnreadCount(): void {
    this.api.get<UnreadCountResponse>('/notifications/unread-count').subscribe({
      next: (res) => this.unreadCount$.next(res.unread_count),
      error: () => {}
    });
  }

  markRead(id: string): void {
    this.api.patch(`/notifications/${id}/read`).subscribe({
      next: () => this.loadUnreadCount(),
      error: () => {}
    });
  }

  markAllRead(): void {
    this.api.patch('/notifications/read-all').subscribe({
      next: () => this.unreadCount$.next(0),
      error: () => {}
    });
  }

  ngOnDestroy(): void {
    this.pollSubscription?.unsubscribe();
  }
}
