import { Injectable } from '@angular/core';
import { environment } from '../../environment';
import { Subject } from 'rxjs';

export interface WebSocketMessage {
  action?: string;
  room_code?: string;
  players?: string[];
  error?: string;
  type?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private messageSubject = new Subject<WebSocketMessage>(); // ✅ Observable for incoming messages
  public messages$ = this.messageSubject.asObservable(); // ✅ Public stream

  connect(endpoint: string): void {
    const wsUrl = `${environment.wsUrl}/${endpoint}`;

    if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => console.log("✅ WebSocket connected:", wsUrl);
      this.socket.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log("📩 Message received:", message);
        this.messageSubject.next(message); // ✅ Send data to subscribers
      };
      this.socket.onerror = (error) => console.error("❌ WebSocket error:", error);
      this.socket.onclose = () => console.warn("⚠️ WebSocket connection closed");
    }
  }

  sendMessage(message: WebSocketMessage): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  close(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
