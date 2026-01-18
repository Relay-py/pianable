import fluidsynth


class Instrument:

    def __init__(self, soundfont_path: str, preset=0, volume=30):
        self.current_notes = set()

        self.fs = fluidsynth.Synth()
        self.soundfont_path = soundfont_path
        self.preset = preset
        self.volume = volume

    
    def start(self) -> None:
        self.fs.setting("synth.gain", 2.0)
        self.fs.start()

        sfid = self.fs.sfload(self.soundfont_path)
        self.fs.program_select(0, sfid, 0, self.preset)

    
    def stop(self) -> None:
        self.fs.delete()


    def add_note(self, midi_note: int) -> None:
        self.current_notes.add(midi_note)

        self.fs.noteon(0, midi_note, self.volume)

    
    def remove_note(self, midi_note) -> None:
        if midi_note not in self.current_notes:
            return
        
        self.current_notes()
        self.fs.noteoff(0, midi_note)


    def is_playing(self, string_num: int) -> bool:
        return self.notes[string_num] is not None