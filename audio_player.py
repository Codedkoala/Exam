import os, asyncio, pygame
import edge_tts 

class AudioPlayer:
    def __init__(self, output_dir="audio_exercises"):
        self.output_dir = output_dir
        self.playlist = []
        self.current_idx = 0
        os.makedirs(self.output_dir, exist_ok=True)
        pygame.mixer.init()

    def generate_and_add_tts(self, text, filename):
        safe_filename = f"{len(self.playlist)}_{filename}"
        path = os.path.join(self.output_dir, f"{safe_filename}.mp3")
        
        async def _generate():
            communicate = edge_tts.Communicate(text, "de-DE-KillianNeural", rate="+0%")
            await communicate.save(path)
            
        asyncio.run(_generate())
        self.playlist.append(path)
        return path

    def execute_command(self, cmd):
        if not self.playlist: return "Keine Playlist"
        
        if cmd == 'next' and self.current_idx < len(self.playlist) - 1:
            self.current_idx += 1
        elif cmd == 'prev' and self.current_idx > 0:
            self.current_idx -= 1
            
        if cmd in ['next', 'prev', 'play']:
            pygame.mixer.music.load(self.playlist[self.current_idx])
            pygame.mixer.music.play()
        elif cmd == 'pause':
            if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()
            
        return f"Track: {self.current_idx + 1} von {len(self.playlist)}"