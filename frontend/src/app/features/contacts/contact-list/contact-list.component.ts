import { Component, Input, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';
import { ContactService } from '../services/contact.service';
import { Contact } from '../models/contact.model';
import { ContactFormComponent } from '../contact-form/contact-form.component';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-contact-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatIconModule],
  templateUrl: './contact-list.component.html',
  styleUrl: './contact-list.component.scss'
})
export class ContactListComponent implements OnInit {
  @Input({ required: true }) propertyId!: string;

  private contactService = inject(ContactService);
  private dialog = inject(MatDialog);

  contacts: Contact[] = [];
  displayedColumns = ['name', 'contact_type', 'email', 'phone', 'actions'];
  loading = true;

  ngOnInit(): void {
    this.loadContacts();
  }

  loadContacts(): void {
    this.loading = true;
    this.contactService.getByProperty(this.propertyId).subscribe({
      next: (contacts) => {
        this.contacts = contacts;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  addContact(): void {
    const dialogRef = this.dialog.open(ContactFormComponent, {
      width: '500px',
      data: { propertyId: this.propertyId }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) this.loadContacts();
    });
  }

  editContact(contact: Contact): void {
    const dialogRef = this.dialog.open(ContactFormComponent, {
      width: '500px',
      data: { propertyId: this.propertyId, contact }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) this.loadContacts();
    });
  }

  deleteContact(contact: Contact): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Contact',
        message: `Delete contact "${contact.first_name} ${contact.last_name}"?`,
        confirmText: 'Delete'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.contactService.delete(contact.id).subscribe({
          next: () => this.loadContacts()
        });
      }
    });
  }
}
