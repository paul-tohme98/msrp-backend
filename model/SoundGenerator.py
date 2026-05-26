from pydub import AudioSegment
from midi2audio import FluidSynth
from pydub import AudioSegment
from mido import MidiFile, MidiTrack, Message
import subprocess


class SoundGenerator:

    @classmethod
    def saveToTextFile(self, outputFile, listOutput):
        with open(outputFile, 'w') as file:
            # Iterate over the elements of the list
            for item in listOutput:
                # Write each item followed by a newline character
                file.write(str(f"{item}" + "\n"))


    @classmethod
    def getPitchNumber(self, note):
        scaleMapping = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
        accidentals = {'natural': 0, 'sharp': 1, 'flat': -1, 'double-sharp': 2, 'double-flat': -2}

        pitch, octave = note[0][0].lower(), (int(note[0][1]) + 1)

        basePitch = scaleMapping['c'] + ((octave + 1) * 12)  # Assuming octave 3 is the base octave
        pitchInScale = (scaleMapping[pitch] + accidentals.get('', 0)) % 12
        return basePitch + pitchInScale


    @classmethod
    def playMidiNotes(self, session, musicData, instrument):
        inst = session.new_part(instrument)
        
        for item in musicData:
            if isinstance(item, tuple):
                pitchNumber = self.getPitchNumber(item)
                volume = 20.0  # Adjust the volume as needed
                duration = item[1]
                inst.play_note(pitchNumber, volume, duration)
                #time.sleep(max(0.0, duration - 0.05))  # Sleep slightly less than the duration
            elif isinstance(item, list):
                pitches = []
                for note in item:
                    pitchNumber = self.getPitchNumber(note)
                    pitches.append(pitchNumber)
                    volume = 20.0  # Adjust the volume as needed
                    duration = note[1]
                    #time.sleep(max(0.0, note.duration - 0.05))  # Sleep slightly less than the duration
                inst.play_chord(pitches, volume, duration)  # Play all chord notes simultaneously
            # elif isinstance(item, Rest):
            #     time.sleep(item.duration)

    @classmethod
    def saveAsMp3(self, session, musicData, instrument):
        inst = session.new_part(instrument)

        # Create a MIDI file
        midiFile = MidiFile()
        track = MidiTrack()
        midiFile.tracks.append(track)

        for item in musicData:
            if isinstance(item, tuple):
                pitchNumber = self.getPitchNumber(item)
                velocity = int(127 * 5.0 / 10.0)  # Adjust velocity based on volume
                duration = int(item[1] * 1000)  # Convert seconds to milliseconds
                track.append(Message('note_on', note=pitchNumber, velocity=velocity, time=0))
                track.append(Message('note_off', note=pitchNumber, velocity=velocity, time=duration))
            elif isinstance(item, list):
                for note in item:
                    pitchNumber = self.getPitchNumber(note)
                    velocity = int(127 * 1.0 / 10.0)  # Adjust velocity based on volume
                    duration = int(note[1] * 1000)  # Convert seconds to milliseconds
                    track.append(Message('note_on', note=pitchNumber, velocity=velocity, time=0))
                    track.append(Message('note_off', note=pitchNumber, velocity=velocity, time=duration))
            # elif isinstance(item, Rest):
            #     time.sleep(item.duration)

        # Save the MIDI file
        tempMidiFilename = 'temp.mid'
        file = midiFile.save(tempMidiFilename)

        # # Convert the MIDI file to WAV using FluidSynth
        # fluidsynth = FluidSynth()
        # fluidsynth.midi_to_audio(tempMidiFilename, 'temp.mp3')
        
        # # Load the WAV file and export it as an MP3 file
        # audio = AudioSegment.from_mp3('temp.mp3')
        # audio.export("output.mp3", format='mp3')

        print(f'Saved the soundtrack as {tempMidiFilename}')

        return file

