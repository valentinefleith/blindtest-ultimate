import { Component } from '@angular/core';
import { RouterModule } from '@angular/router'; // Import du module de routing

@Component({
  selector: 'app-home',
  standalone: true, // Important pour Angular 17+
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  imports: [RouterModule], // Ajout explicite du module de routing
})
export class HomeComponent {}
