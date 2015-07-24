# Phases of Development

## Phase 1: Always On, Voice Recognition
Implement a system that is always listening for a key phrase (i.e. Jarvis) then captures the command/query and produces a text representation.

### Dependencies
- PocketSphinx. Easiest way is to apt-get install python-pocketsphinx. Other methods are troublesome at the moment.

## Phase 2: Let There Be Light(s)
Create first simple application of JARVIS: a single light/lamp. Must use the full system of intent filters as if it were just one of many apps installed. Actually, create two lights, so the filters must actually route the command appropriately.

## Phase 3: The Bridge
Broadcasting, filtering, and handling "intents," much like the Android OS does. This service would happen on a local area network. What is the appropriate form of communication?