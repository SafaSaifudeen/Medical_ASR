import { Component, HostListener } from '@angular/core';
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
  isDragging: boolean = false; // Variable to track drag state

  constructor(private http: HttpClient) {}

  // Handle file input change
  onFileChange(event: any): void {
    const file = event.target.files[0];
    this.processFile(file);
  }

  // Process the uploaded file
  processFile(file: File | null): void {
    if (file && file.type.startsWith('audio/')) {
      this.fileName = file.name;
      this.audioUrl = URL.createObjectURL(file); // Create a URL for the audio file
      this.uploadFile(file); // Trigger file upload
    } else if (file) {
      alert('Please upload only audio files.');
      this.fileName = ''; // Reset if file is not an audio file
      this.audioUrl = null;
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

  // Download the transcription as a text file
  downloadTranscription(): void {
    if (!this.transcription) {
      return; // Don't proceed if there's no transcription
    }

    // Create a blob with the transcription text
    const blob = new Blob([this.transcription], { type: 'text/plain' });
    
    // Create a download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    
    // Set the filename based on the audio file name or use a default
    const fileName = this.fileName 
      ? this.fileName.replace(/\.[^/.]+$/, '') + '_transcript.txt' 
      : 'transcript.txt';
    a.download = fileName;
    
    // Append to the document, trigger the download, and clean up
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // Copy transcription to clipboard
  copyToClipboard(): void {
    if (!this.transcription) {
      return; // Don't proceed if there's no transcription
    }

    navigator.clipboard.writeText(this.transcription)
      .then(() => {
        // Show a temporary success message
        const copyButton = document.querySelector('.copy-button') as HTMLElement;
        if (copyButton) {
          const originalText = copyButton.innerHTML;
          copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
          setTimeout(() => {
            copyButton.innerHTML = originalText;
          }, 2000);
        }
      })
      .catch(err => {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy to clipboard');
      });
  }

  // Drag and drop event handlers
  @HostListener('dragover', ['$event'])
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  @HostListener('dragleave', ['$event'])
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  @HostListener('drop', ['$event'])
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      this.processFile(file);
    }
  }
}
