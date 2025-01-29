import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { PlaylistComponent } from '../../components/playlist/playlist.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
  imports: [PlaylistComponent]
})
export class ProfileComponent {
  user: any;

  constructor(private authService: AuthService, private router: Router) {
    this.user = this.authService.getUserInfo();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
