import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css'],
  imports: [NgIf]
})
export class MainComponent {
  fileName: string = ''; // Variable to store the uploaded file name
  transcription: string = ''; // Variable to store transcription
  loading: boolean = false; // Loading state to show spinner or text
  audioUrl: string | null = null; // Variable to store audio file URL

  constructor(private http: HttpClient) {}

  // Handle file input change
  onFileChange(event: any): void {
    const file = event.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      this.fileName = file.name;
      this.audioUrl = URL.createObjectURL(file); // Create a URL for the audio file
      this.uploadFile(file); // Trigger file upload
      event.target.value = ''; // Reset the input field after upload
    } else {
      alert('Please upload only audio files.');
      this.fileName = ''; // Reset if file is not an audio file
      this.audioUrl = null;
      event.target.value = ''; // Reset the input field
    }
  }

  // Upload the file to the backend
  uploadFile(file: File): void {
    const formData = new FormData();
    formData.append('file', file);

    this.loading = true; // Set loading to true when the request starts

    this.http.post('http://localhost:5001/transcribe', formData).subscribe(
      (response: any) => {
        this.transcription = response.transcription; // Handle the transcription result
        this.loading = false; // Set loading to false when the request completes
      },
      (error) => {
        console.error('Error:', error);
        alert('There was an error with the transcription process.');
        this.loading = false; // Set loading to false when an error occurs
      }
    );
  }
}
