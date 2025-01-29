import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Song {
  id: number;
  title: string;
  artist: string;
  albumCover: string;
  previewUrl: string;
}

@Component({
  selector: 'app-playlist',
  standalone: true,
  templateUrl: './playlist.component.html',
  styleUrls: ['./playlist.component.scss'],
  imports: [CommonModule, FormsModule] // ✅ Add FormsModule for search input
})
export class PlaylistComponent implements OnInit {
  playlist: Song[] = [];
  searchResults: Song[] = [];
  searchQuery: string = '';
  audio = new Audio();
  currentlyPlaying: number | null = null;

  constructor(private http: HttpClient, private authService: AuthService) {}

  ngOnInit(): void {
    this.fetchPlaylist();
  }

  fetchPlaylist(): void {
    const headers = {
      Authorization: `Bearer ${this.authService.getToken()}` // ✅ Include token
    };

    this.http.get<any>(`http://localhost:8000/api/playlists/`, { headers })
      .subscribe(response => {
        console.log("Fetched playlist:", response); // ✅ Debugging log
        this.playlist = response.songs || []; // ✅ Update playlist if available
      }, error => {
        console.error('Error fetching playlist:', error);
      });
  }

  searchSongs(): void {
    if (this.searchQuery.trim() === '') {
      this.searchResults = [];
      return;
    }

    this.http.get<Song[]>(`http://localhost:8000/api/songs/search?q=${this.searchQuery}`)
      .subscribe(response => {
        this.searchResults = response;
      }, error => {
        console.error('Error fetching search results:', error);
      });
  }

  addSongToPlaylist(song: any): void {
    const userId = this.authService.getUserInfo()?.user_id;
    if (!userId) return;

    const payload = {
      deezer_track_id: song.deezer_track_id,
      title: song.title,
      artist: song.artist,
      preview_url: song.preview_url,
      album_cover: song.album_cover,
    };

    const headers = {
      Authorization: `Bearer ${this.authService.getToken()}` // ✅ Include token
    };

    console.log("Adding song with token:", headers); // ✅ Debug log

    this.http.post(`http://localhost:8000/api/playlists/songs/`, payload, { headers })
      .subscribe(() => {
        this.playlist.push(song); // ✅ Update UI instantly
        console.log("Song added successfully!");
      }, error => {
        console.error('Error adding song to playlist:', error);
      });
  }

  removeSong(songId: number): void {
    this.http.delete(`http://localhost:8000/api/playlists/${songId}`)
      .subscribe(() => {
        this.playlist = this.playlist.filter(song => song.id !== songId);
      }, error => {
        console.error('Error removing song:', error);
      });
  }

  playPreview(song: Song): void {
    if (this.currentlyPlaying === song.id) {
      this.audio.pause();
      this.currentlyPlaying = null;
    } else {
      this.audio.src = song.previewUrl;
      this.audio.play();
      this.currentlyPlaying = song.id;
    }
  }
}
