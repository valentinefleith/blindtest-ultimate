import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import {CommonModule} from '@angular/common'; // Import du module de routing
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true, // Important pour Angular 17+
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  imports: [RouterModule, CommonModule], // Ajout explicite du module de routing
})
export class HomeComponent implements OnInit {
  isLoggedIn = false;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.authService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status
    });
  }
}
