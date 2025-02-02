import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { WebSocketService, WebSocketMessage } from '../../services/websocket.service'; // ✅ Import WebSocketMessage
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  imports: [CommonModule, RouterModule, FormsModule],
})
export class HomeComponent implements OnInit {
  isLoggedIn = false;
  roomCode = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private wsService: WebSocketService
  ) {}

  ngOnInit() {
    this.authService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });

    // ✅ Subscribe to WebSocket messages with the correct type
    this.wsService.messages$.subscribe((data: WebSocketMessage) => {
      if (data.action === "room_created") {
        console.log("🎉 Room Created:", data.room_code);
        this.router.navigate([`/room/${data.room_code}`]);
      }
    });
  }

  createRoom(): void {
    const token = this.authService.getToken();
    this.wsService.connect(`ws/create?token=${token}`);
    this.wsService.sendMessage({ action: 'create_room' });
  }


  joinRoom(): void {
    if (this.roomCode.trim() === '') {
      alert("Please enter a valid room code!");
      return;
    }

    // ✅ Check if the room exists before navigating
    fetch(`http://localhost:8000/api/rooms/exists/${this.roomCode}`)
      .then(response => {
        if (!response.ok) {
          throw new Error("Room not found");
        }
        return response.json();
      })
      .then(() => {
        console.log("✅ Room exists! Redirecting...");
        this.router.navigate([`/room/${this.roomCode}`]); // ✅ Only navigate if room exists
      })
      .catch(() => {
        alert("❌ This room does not exist!");
      });
  }
}
