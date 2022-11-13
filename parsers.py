from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Page:
    """Class for a wiki page."""
    title: str = ""
    url: str = ""


@dataclass_json
@dataclass
class Category:
    """Class for a wiki category."""
    title: str = ""
    url: str = ""
    pages: list[Page] = ""


wiki_pages = ['Overview & Installation / Installation Guide', 'Overview & Installation / Project Settings',
              'Overview & Installation / URP / HDRP Render Pipelines', 'Overview & Installation / Demo Scene',
              'Device & SDK Support / Device Support', 'Device & SDK Support / Meta Quest & Rift S',
              'Device & SDK Support / SteamVR & OpenVR', 'Device & SDK Support / HTC Vive',
              'Device & SDK Support / Windows Mixed Reality', 'Device & SDK Support / Pico',
              'Device & SDK Support / Custom Input', 'VRIF Core Components / Grabber',
              'VRIF Core Components / Grabbable', 'VRIF Core Components / Grabbable Events',
              'VRIF Core Components / Climbable', 'VRIF Core Components / Input Bridge',
              'VRIF Core Components / Player Teleport', 'VRIF Core Components / Smooth Locomotion',
              'VRIF Core Components / Player Rotation', 'VRIF Core Components / BNGPlayerController',
              'VRIF General / Buttons, Switches & Levers', 'VRIF General / Grab Points', 'VRIF General / Snap Zones',
              'VRIF General / VR Hands', 'VRIF General / Hand Poses', 'VRIF Extras / VR Emulator',
              'VRIF Extras / Arms and Body IK', 'VRIF Extras / Slow Motion', 'VRIF Extras / Dealing & Taking Damage',
              'VRIF Integrations / SteamVR', 'VRIF Integrations / Oculus Integration', 'VRIF Integrations / FinalIK',
              'VRIF Integrations / Emerald AI', 'VRIF Integrations / Curved UI', 'VRIF Integrations / Photon PUN2',
              'VRIF Integrations / VR Builder', 'Tutorials / Creating a Grabbable Object',
              'Tutorials / Replacing Weapon Models', 'Tips & Tricks / Upgrading to New Versions',
              'Tips & Tricks / Common Issues & Fixes', 'Tips & Tricks / Tips & Guidelines']
