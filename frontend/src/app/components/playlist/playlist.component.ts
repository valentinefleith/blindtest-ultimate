import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Song {
  id: number;
  title: string;
  artist: string;
  album_cover: string;
  preview_url: string;
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
  searchQuery = '';
  audio = new Audio();
  currentlyPlaying: number | null = null;

  constructor(private http: HttpClient, private authService: AuthService, private cdRef: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.fetchPlaylist();
  }

  fetchPlaylist(): void {
    const headers = {
      Authorization: `Bearer ${this.authService.getToken()}` // ✅ Include token
    };

    this.http.get<any>(`http://localhost:8000/api/playlists/`, { headers })
      .subscribe(response => {
        this.playlist = [...response.songs]; // ✅ Update playlist if available
        this.cdRef.detectChanges();
      }, error => {
        console.error('Error fetching playlist:', error);
      });
  }

searchSongs(): void {
  if (this.searchQuery.trim() === '') {
    this.searchResults = [];
    this.cdRef.detectChanges();
    return;
  }

  this.http.get<any[]>(`http://localhost:8000/api/songs/search?q=${this.searchQuery}`)
    .subscribe(response => {
      console.log("🎵 API Response:", response);

      this.searchResults = response.map(song => ({
        ...song,
        album_cover: song.album_cover
      }));

      console.log("🔍 Processed Search Results with Fixed URLs:", this.searchResults);
      this.cdRef.detectChanges(); // ✅ Force UI refresh
    }, error => {
      console.error('❌ Error fetching search results:', error);
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
    album_cover: song.album_cover, // ✅ Use album_cover (not albumCover)
  };

  const headers = {
    Authorization: `Bearer ${this.authService.getToken()}`
  };

  this.http.post(`http://localhost:8000/api/playlists/songs/`, payload, { headers })
    .subscribe(() => {
      this.playlist.push(song); // ✅ Instantly update UI
      this.searchQuery = ''; // ✅ Clear search bar
      this.searchResults = []; // ✅ Hide search results
      this.cdRef.detectChanges(); // ✅ Force UI refresh
      console.log("✅ Song added successfully!");
    }, error => {
      console.error('❌ Error adding song to playlist:', error);
    });
}

  removeSong(song: any): void {
    if (!song || !song.deezer_track_id) {
      console.error("❌ Error: Missing song data or ID", song);
      return;
    }

    const headers = {
      Authorization: `Bearer ${this.authService.getToken()}`
    };

    console.log(`🗑️ Deleting song with ID: ${song.deezer_track_id}`);

    // ✅ Stop playback if the removed song is currently playing
    if (this.currentlyPlaying === song.deezer_track_id) {
      this.audio.pause();
      this.currentlyPlaying = null;
    }

    this.http.delete(`http://localhost:8000/api/playlists/songs/${song.deezer_track_id}`, { headers })
      .subscribe(() => {
        console.log("✅ Song removed successfully!");

        // ✅ Remove song from the playlist in the UI
        this.playlist = this.playlist.filter(s => s.id !== song.deezer_track_id);
        this.cdRef.detectChanges(); // ✅ Force UI refresh
      }, error => {
        console.error('❌ Error removing song:', error);
      });
  }

  playPreview(song: any): void {
    if (!song.preview_url) {
      console.error("❌ Error: Missing preview URL for song", song);
      return;
    }

    // ✅ If the same song is already playing, pause it
    if (this.currentlyPlaying === song.deezer_track_id) {
      this.audio.pause();
      this.currentlyPlaying = null;
      console.log("⏸️ Playback paused");
      return;
    }

    // ✅ If another song is playing, stop it first
    if (this.audio) {
      this.audio.pause();
      this.currentlyPlaying = null;
    }

    // ✅ Create new audio and play the preview
    this.audio = new Audio(song.preview_url);
    this.audio.play()
      .then(() => {
        this.currentlyPlaying = song.deezer_track_id;
        console.log("▶️ Now playing:", song.title);
        this.audio.ontimeupdate = () => this.cdRef.detectChanges();

        // ✅ Reset button when the song ends
        this.audio.onended = () => {
          this.currentlyPlaying = null;
          this.cdRef.detectChanges(); // Force UI update
        };
      })
      .catch(error => {
        console.error("❌ Error playing song:", error);
      });

    this.cdRef.detectChanges(); // Force UI update
  }

getProgress(song: any): string {
  if (this.currentlyPlaying === song.deezer_track_id && this.audio) {
    const progress = (this.audio.currentTime / this.audio.duration) * 100;
    return `${progress}%`;
  }
  return "0%";
}

  refreshPlaylist(): void {
    console.log("🔄 Refreshing playlist...");

    // ✅ Stop any currently playing audio
    if (this.audio) {
      this.audio.pause();
      this.currentlyPlaying = null; // Reset UI state
    }

    const headers = {
      Authorization: `Bearer ${this.authService.getToken()}`
    };

    this.http.get<any>(`http://localhost:8000/api/playlists/`, { headers })
      .subscribe(response => {
        console.log("✅ Playlist refreshed:", response);
        this.playlist = [...response.songs]; // ✅ Force UI update
        this.cdRef.detectChanges(); // ✅ Ensure UI updates
      }, error => {
        console.error('❌ Error refreshing playlist:', error);
      });
  }
}
