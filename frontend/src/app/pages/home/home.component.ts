import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { trigger, state, style, animate, transition } from '@angular/animations';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
  animations: [
    trigger('fadeInOut', [
      state('void', style({
        opacity: 0,
        transform: 'translateY(20px)'
      })),
      transition(':enter', [
        animate('0.6s ease-out', style({
          opacity: 1,
          transform: 'translateY(0)'
        }))
      ])
    ]),
    trigger('cardHover', [
      state('normal', style({
        transform: 'scale(1)',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      })),
      state('hovered', style({
        transform: 'scale(1.05)',
        boxShadow: '0 8px 15px rgba(0, 0, 0, 0.2)'
      })),
      transition('normal <=> hovered', animate('200ms ease-in-out'))
    ])
  ]
})
export class HomeComponent {
  cardStates: { [key: string]: 'normal' | 'hovered' } = {
    transcription: 'normal',
    documentation: 'normal',
    upload: 'normal'
  };

  onCardHover(card: string, isHovered: boolean) {
    this.cardStates[card] = isHovered ? 'hovered' : 'normal';
  }
}
