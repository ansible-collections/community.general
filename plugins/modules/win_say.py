#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Jon Hawkesworth (@jhawkesworth) <figs@unity.demon.co.uk>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# this is a windows documentation stub.  actual code lives in the .ps1
# file of the same name

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_say
short_description: Text to speech module for Windows to speak messages and optionally play sounds
description:
    - Uses .NET libraries to convert text to speech and optionally play .wav sounds.  Audio Service needs to be running and some kind of speakers or
      headphones need to be attached to the windows target(s) for the speech to be audible.
options:
  msg:
    description:
      - The text to be spoken.
      - Use either C(msg) or C(msg_file).
      - Optional so that you can use this module just to play sounds.
    type: str
  msg_file:
    description:
      - Full path to a windows format text file containing the text to be spoken.
      - Use either C(msg) or C(msg_file).
      - Optional so that you can use this module just to play sounds.
    type: path
  voice:
    description:
      - Which voice to use. See notes for how to discover installed voices.
      - If the requested voice is not available the default voice will be used.
        Example voice names from Windows 10 are C(Microsoft Zira Desktop) and C(Microsoft Hazel Desktop).
    type: str
  speech_speed:
    description:
      - How fast or slow to speak the text.
      - Must be an integer value in the range -10 to 10.
      - -10 is slowest, 10 is fastest.
    type: int
    default: 0
  start_sound_path:
    description:
      - Full path to a C(.wav) file containing a sound to play before the text is spoken.
      - Useful on conference calls to alert other speakers that ansible has something to say.
    type: path
  end_sound_path:
    description:
      - Full path to a C(.wav) file containing a sound to play after the text has been spoken.
      - Useful on conference calls to alert other speakers that ansible has finished speaking.
    type: path
notes:
   - Needs speakers or headphones to do anything useful.
   - |
     To find which voices are installed, run the following Powershell commands.

                 Add-Type -AssemblyName System.Speech
                 $speech = New-Object -TypeName System.Speech.Synthesis.SpeechSynthesizer
                 $speech.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo }
                 $speech.Dispose()

   - Speech can be surprisingly slow, so it's best to keep message text short.
seealso:
- module: win_msg
- module: win_toast
author:
- Jon Hawkesworth (@jhawkesworth)
'''

EXAMPLES = r'''
- name: Warn of impending deployment
  win_say:
    msg: Warning, deployment commencing in 5 minutes, please log out.

- name: Using a different voice and a start sound
  win_say:
    start_sound_path: C:\Windows\Media\ding.wav
    msg: Warning, deployment commencing in 5 minutes, please log out.
    voice: Microsoft Hazel Desktop

- name: With start and end sound
  win_say:
    start_sound_path: C:\Windows\Media\Windows Balloon.wav
    msg: New software installed
    end_sound_path: C:\Windows\Media\chimes.wav

- name: Text from file example
  win_say:
    start_sound_path: C:\Windows\Media\Windows Balloon.wav
    msg_file: AppData\Local\Temp\morning_report.txt
    end_sound_path: C:\Windows\Media\chimes.wav
'''

RETURN = r'''
message_text:
    description: The text that the module attempted to speak.
    returned: success
    type: str
    sample: "Warning, deployment commencing in 5 minutes."
voice:
    description: The voice used to speak the text.
    returned: success
    type: str
    sample: Microsoft Hazel Desktop
voice_info:
    description: The voice used to speak the text.
    returned: when requested voice could not be loaded
    type: str
    sample: Could not load voice TestVoice, using system default voice
'''
