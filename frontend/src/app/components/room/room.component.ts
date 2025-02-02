import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { WebSocketService } from '../../services/websocket.service';
import { AuthService } from '../../services/auth.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-room',
  standalone: true,
  templateUrl: './room.component.html',
  styleUrls: ['./room.component.scss'],
  imports: [CommonModule]
})
export class RoomComponent implements OnInit, OnDestroy {
  roomCode = '';
  players: string[] = []; // ✅ List of connected players
  isOwner = false;
  gameStarted = false;
  username = ''; // ✅ Get logged-in user's username
  private wsSubscription: Subscription | null = null; // ✅ Store WebSocket subscription

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private wsService: WebSocketService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.roomCode = this.route.snapshot.paramMap.get('room_code') || '';
    this.username = this.authService.getUserInfo()?.username || ''; // ✅ Get logged-in username

    if (!this.roomCode) {
      this.router.navigate(['/']); // ✅ Redirect to home if no room code
      return;
    }

    this.connectToRoom();
  }

  connectToRoom(): void {
    const token = this.authService.getToken();
    this.wsService.connect(`ws/join/${this.roomCode}?token=${token}`);

    // ✅ Subscribe to WebSocket messages AFTER connecting
    this.wsSubscription = this.wsService.messages$.subscribe((msg) => {
      console.log("📩 WebSocket Message:", msg);

      if (msg.type === 'players') {
        this.players = msg.players || []; // ✅ Ensure it's not undefined
        this.isOwner = this.players[0] === this.username; // ✅ Detect if user is owner
      } else if (msg.error) {
        alert(`❌ Error: ${msg.error}`);
        this.router.navigate(['/']);
      }
    });
  }

  startGame(): void {
    if (!this.isOwner) return;

    const token = this.authService.getToken();
    this.wsService.connect(`ws/start/${this.roomCode}?token=${token}`);
    this.wsService.sendMessage({ action: 'start_game' });

    this.wsService.messages$.subscribe((msg) => {
      if (msg.action === 'game_started') {
        this.gameStarted = true;
      }
    });
  }

  disconnect(): void {
    this.wsService.close();
    this.router.navigate(['/']);
  }

  ngOnDestroy(): void {
    this.wsSubscription?.unsubscribe(); // ✅ Prevent memory leaks
  }
}
